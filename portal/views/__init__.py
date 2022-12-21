from typing import Any, Dict
from django.views.generic import ListView
from ..models import Semester, User
from django.shortcuts import get_object_or_404


def load_semesters(request):
    return {"semesters": Semester.objects.all()}


class SemesterFilteredListView(ListView):
    """
    Render some list of objects, set by self.model or self.queryset. self.queryset can actually be any iterable of items, not just a queryset.

    If `semester` query parameter is present AND valid:
        - finds semester and passes it to template as `target_semester`
        - filters queryset with `<self.semester_filter_key>=target_semester`

    If `semester`is present and INVALID:
        - throws a 404

    Example:
    ```
    class ProjectIndexView(SemesterFilteredListView):
        template_name = "portal/projects/index.html"
        context_object_name = "projects"

        # Default to all approved users
        queryset = Project.objects.filter(is_approved=True)
        # Filter projects where `enrollments__semester` == the semester with the ID passed in the URL (if present)
        semester_filter_key = "enrollments__semester"
    ```
    """

    semester_filter_key = "semester"
    """The key to match with the semester object when filtering."""

    def get_queryset(self):
        """Default to queryset, and filters down to a particular semester if requested."""
        queryset = super().get_queryset()

        semester_id = self.request.GET.get("semester")
        if semester_id:
            self.target_semester = get_object_or_404(Semester, pk=semester_id)

            return queryset.filter(**{self.semester_filter_key: self.target_semester})
        else:
            self.target_semester = None

        return queryset

    def get_context_data(self, **kwargs):
        """Expose `target_semester` to the template if present."""
        data = super().get_context_data(**kwargs)
        data["target_semester"] = self.target_semester
        return data
