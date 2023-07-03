# Generated by Django 4.2.2 on 2023-07-03 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0040_alter_mentorapplication_skills"),
    ]

    operations = [
        migrations.AddField(
            model_name="organization",
            name="logo_url",
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name="project",
            name="is_approved",
            field=models.BooleanField(
                default=True,
                help_text="Whether the project has been approved by Mentors/Coordinators to participate in RCOS",
                verbose_name="approved?",
            ),
        ),
        migrations.AlterField(
            model_name="projectproposal",
            name="url",
            field=models.URLField(
                help_text="Link to the proposal document, typically a Google Doc. Make sure it is publicly viewable!",
                verbose_name="Proposal Document URL",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[("rpi", "RPI User"), ("external", "External User")],
                default="external",
                max_length=30,
            ),
        ),
    ]
