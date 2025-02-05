"""Views related to projects."""
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.cache import cache
from django.core.paginator import EmptyPage, InvalidPage, PageNotAnInteger, Paginator
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic.edit import CreateView
from gql.transport.exceptions import TransportServerError

from portal.checks import (
    CheckUserCanCreateProject,
    CheckUserCanPitchProject,
    CheckUserCanSubmitProjectProposal,
)
from portal.forms import ProjectCreateForm
from portal.services import github

from ..models import (
    Enrollment,
    Organization,
    Project,
    ProjectPitch,
    ProjectProposal,
    Semester,
    User,
)
from . import (
    OrganizationFilteredListView,
    SearchableListView,
    SemesterFilteredListView,
    UserRequiresSetupMixin,
    target_semester_context,
)


@login_required
def project_lead_index(request: HttpRequest) -> HttpResponse:
    """Shows users options to either start a new project or continue an owned project."""

    check = CheckUserCanCreateProject().check(
        request.user, semester=cache.get("active_semester")
    )

    if not check.passed:
        messages.error(
            request,
            f"You cannot lead a project at this time: {check.fail_reason} {check.fix}",
        )
        return redirect(reverse("projects_index"))

    return TemplateResponse(request, "portal/projects/lead_index.html", {})


class ProjectIndexView(
    SearchableListView, OrganizationFilteredListView, SemesterFilteredListView
):
    template_name = "portal/projects/index.html"
    context_object_name = "projects"
    paginate_by = 25

    # Default to all approved projects
    queryset = (
        Project.objects.filter(is_approved=True)
        .prefetch_related("tags", "pitches")
        .select_related("owner", "organization")
    )
    semester_filter_key = "enrollments__semester"
    search_fields = (
        "name",
        "owner__first_name",
        "owner__last_name",
        "owner__rcs_id",
        "description",
        "tags__name",
    )

    def get_queryset(self):
        """Apply filters (semester is already handled)."""
        queryset = super().get_queryset()

        self.is_seeking_members = self.request.GET.get("is_seeking_members") == "yes"
        if self.is_seeking_members:
            queryset = queryset.filter(pitches__semester=self.target_semester)
            self.is_seeking_members = True

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["organizations"] = Organization.objects.all()
        data["is_seeking_members"] = self.is_seeking_members
        data["total_count"] = self.get_queryset().count()
        paginator = Paginator(self.get_queryset(), self.paginate_by)

        page = self.request.GET.get("page")

        try:
            projects = paginator.page(page)
        except PageNotAnInteger:
            projects = paginator.page(1)
        except (EmptyPage, InvalidPage):
            projects = paginator.page(paginator.num_pages)

        projects_rows = []
        enrollments = Enrollment.objects.filter(project__in=projects).select_related(
            "user"
        )
        if self.target_semester:
            enrollments = enrollments.filter(
                semester=self.target_semester
            ).select_related("semester")

            if self.request.user.is_authenticated:
                data["can_create_project_check"] = CheckUserCanCreateProject().check(
                    self.request.user, self.target_semester
                )

        for project in projects:
            projects_row = {
                "project": project,
                "enrollments": len(
                    [e for e in enrollments if e.project_id == project.pk]
                ),
            }
            if self.target_semester:
                projects_row["leads"] = [
                    e
                    for e in enrollments
                    if e.project_id == project.pk and e.is_project_lead is True
                ]
                projects_row["pitch"] = next(
                    (
                        pitch
                        for pitch in project.pitches.all()
                        if pitch.semester_id == self.target_semester.pk
                    ),
                    None,
                )
            projects_rows.append(projects_row)

        data["projects_rows"] = projects_rows

        return data


def project_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """Fetches a project and its details either at the semester level or aggregated across all semesters."""

    project: Project = get_object_or_404(
        Project.objects.approved()
        .prefetch_related("tags", "pitches")
        .select_related("owner", "organization"),
        slug=slug,
    )
    context: dict[str, Any] = {"project": project} | target_semester_context(request)

    if request.user.is_authenticated:
        active_enrollment = request.user.get_active_enrollment()
        is_owner_or_lead = (
            (active_enrollment.project == project and active_enrollment.is_project_lead)
            if active_enrollment
            else False
        )
        context["is_owner_or_lead"] = is_owner_or_lead

        # Populate all enrolled students RCS IDs for easy adding team members
        if is_owner_or_lead:
            context[
                "enrolled_rcs_ids"
            ] = active_enrollment.semester.students.values_list("rcs_id", flat=True)

    # Fetch enrollments for either target semester or teams across semesters
    if "target_semester" in context:
        context["target_semester_enrollments"] = project.get_semester_team(
            context["target_semester"]
        )
    else:
        context["enrollments_by_semester"] = project.get_all_teams()

    # Fetch project repositories
    try:
        context["repositories"] = project.get_repositories(github.client_factory())
    except TransportServerError:
        context["repositories"] = []

    return TemplateResponse(request, "portal/projects/detail.html", context)


@login_required
def modify_project_team(request: HttpRequest, slug: str) -> HttpResponse:
    """Add/remove team members for a project."""

    project = get_object_or_404(Project.objects.approved(), slug=slug)

    semester_id = request.GET["semester"]
    semester = get_object_or_404(Semester.objects.all(), pk=semester_id)

    # Logged in user must be project lead to modify team
    try:
        Enrollment.objects.get(
            semester_id=semester.pk,
            user_id=request.user.pk,
            project_id=project.pk,
            is_project_lead=True,
        )
    except Enrollment.DoesNotExist:
        return HttpResponseForbidden()

    if request.method == "POST":
        action = request.GET["action"]
        rcs_id = request.POST["rcs_id"]

        user = get_object_or_404(User.rpi, rcs_id=rcs_id)

        if action == "add":
            Enrollment.objects.update_or_create(
                user=user,
                semester=semester,
                defaults={"project": project},
            )
            # TODO: Discord DM user
        else:
            raise HttpResponseBadRequest()

    return redirect(
        reverse("projects_detail", args=(slug,)) + "?semester=" + semester_id
    )


class ProjectCreateView(
    SuccessMessageMixin, LoginRequiredMixin, UserRequiresSetupMixin, CreateView
):
    form_class = ProjectCreateForm
    template_name = "portal/projects/create.html"
    success_message = (
        "Your project has been created and you've been enrolled as Project Lead!"
    )

    def get(self, request, *args, **kwargs):
        active_semester = Semester.get_active()

        check = CheckUserCanCreateProject().check(self.request.user, active_semester)

        if not check.passed:
            messages.error(
                self.request,
                f"You are not currently eligible to create new projects: {check.fail_reason} {check.fix}",
            )
            return redirect(reverse("projects_index"))

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        active_semester = Semester.get_active()
        if not CheckUserCanCreateProject().passes(self.request.user, active_semester, None):
            messages.error(
                self.request, "You are not currently eligible to create new projects."
            )
            return redirect(reverse("projects_index"))

        form.instance.owner = self.request.user
        form.instance.organization = self.request.user.organization

        # Enroll user in project as lead

        response = super().form_valid(form)
        Enrollment.objects.update_or_create(
            semester=active_semester,
            user=self.request.user,
            defaults={"is_project_lead": True, "project": form.instance},
        )
        return response


class ProjectAddPitch(CreateView, LoginRequiredMixin, SuccessMessageMixin):
    model = ProjectPitch
    template_name = "portal/projects/pitch.html"
    fields = ["url"]
    success_url = "/"
    success_message = "You project pitch was submitted!"

    def get_context_data(self, **kwargs: Any):
        data = super().get_context_data(**kwargs)
        data["project"] = self.project
        data["semester"] = self.semester
        return data

    def get(self, request, *args: str, **kwargs: Any):
        self.semester = Semester.get_active()
        self.project = Project.objects.get(slug=self.kwargs["slug"])

        check = CheckUserCanPitchProject().check(
            self.request.user, self.semester, self.project
        )
        if not check.passed:
            messages.error(
                self.request,
                f"You are not currently eligible to pitch this project: {check.fail_reason} {check.fix}",
            )
            return redirect(reverse("projects_index"))

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        self.semester = Semester.get_active()
        self.project = Project.objects.get(slug=self.kwargs["slug"])

        check = CheckUserCanPitchProject().check(
            self.request.user, self.semester, self.project
        )
        if not check.passed:
            messages.error(
                self.request,
                f"You are not currently eligible to pitch this project: {check.fail_reason} {check.fix}",
            )
            return redirect(reverse("projects_index"))

        form.instance.semester = self.semester
        form.instance.project = self.project
        return super().form_valid(form)


class ProjectAddProposal(CreateView, LoginRequiredMixin, SuccessMessageMixin):
    model = ProjectProposal
    template_name = "portal/projects/proposal.html"
    fields = ["url"]
    success_url = "/"
    success_message = "Your project proposal document was submitted!"

    def get_context_data(self, **kwargs: Any):
        data = super().get_context_data(**kwargs)
        data["project"] = self.project
        data["semester"] = self.semester
        return data

    def get(self, request, *args: str, **kwargs: Any):
        self.semester = Semester.get_active()
        self.project = Project.objects.get(slug=self.kwargs["slug"])

        # Check permission to submit proposal
        check = CheckUserCanSubmitProjectProposal().check(
            self.request.user, self.semester, self.project
        )
        if not check.passed:
            messages.error(
                self.request,
                f"You are not currently eligible to submit a project proposal: {check.fail_reason} {check.fix}",
            )
            return redirect(reverse("projects_index"))

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        self.semester = Semester.get_active()
        self.project = Project.objects.get(slug=self.kwargs["slug"])

        # Check permission to submit proposal
        check = CheckUserCanSubmitProjectProposal().check(
            self.request.user, self.semester, self.project
        )
        if not check.passed:
            messages.error(
                self.request,
                f"You are not currently eligible to submit a project proposal: {check.fail_reason} {check.fix}",
            )
            return redirect(reverse("projects_index"))

        form.instance.semester = self.semester
        form.instance.project = self.project
        return super().form_valid(form)
