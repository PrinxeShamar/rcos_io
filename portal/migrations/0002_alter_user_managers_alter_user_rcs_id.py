# Generated by Django 4.1.4 on 2023-01-18 16:30

from django.db import migrations, models

import portal.models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="user",
            managers=[
                ("students", portal.models.RPIUserManager()),
                ("objects", portal.models.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name="user",
            name="rcs_id",
            field=models.CharField(
                blank=True,
                help_text="If the user is an RPI user, their RCS ID.",
                max_length=30,
                null=True,
                unique=True,
                verbose_name="RCS ID",
            ),
        ),
    ]
