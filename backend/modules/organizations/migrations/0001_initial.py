import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


MODEL_NAMES = ("organization", "organizationmembership")


def move_content_types(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    manager = ContentType.objects.using(schema_editor.connection.alias)

    if manager.filter(
        app_label="organizations",
        model__in=MODEL_NAMES,
    ).exists():
        raise RuntimeError(
            "organizations ContentTypes already exist. "
            "Inspect them before transferring the existing records."
        )

    manager.filter(
        app_label="workflows",
        model__in=MODEL_NAMES,
    ).update(app_label="organizations")


def reverse_content_types(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    manager = ContentType.objects.using(schema_editor.connection.alias)

    if manager.filter(
        app_label="workflows",
        model__in=MODEL_NAMES,
    ).exists():
        raise RuntimeError(
            "workflows ContentTypes already exist. "
            "Cannot safely reverse the transfer."
        )

    manager.filter(
        app_label="organizations",
        model__in=MODEL_NAMES,
    ).update(app_label="workflows")


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("workflows", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="Organization",
                    fields=[
                        (
                            "id",
                            models.BigAutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name="ID",
                            ),
                        ),
                        ("name", models.CharField(max_length=150)),
                        ("slug", models.SlugField(max_length=180, unique=True)),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                        ("updated_at", models.DateTimeField(auto_now=True)),
                        (
                            "created_by",
                            models.ForeignKey(
                                null=True,
                                on_delete=django.db.models.deletion.SET_NULL,
                                related_name="created_organizations",
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                    ],
                    options={
                        "db_table": "workflows_organization",
                        "ordering": ["name"],
                        "verbose_name": "Organization",
                        "verbose_name_plural": "Organizations",
                    },
                ),
                migrations.CreateModel(
                    name="OrganizationMembership",
                    fields=[
                        (
                            "id",
                            models.BigAutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name="ID",
                            ),
                        ),
                        (
                            "role",
                            models.CharField(
                                choices=[
                                    ("owner", "Owner"),
                                    ("admin", "Admin"),
                                    ("member", "Member"),
                                ],
                                default="member",
                                max_length=20,
                            ),
                        ),
                        ("joined_at", models.DateTimeField(auto_now_add=True)),
                        (
                            "organization",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="memberships",
                                to="organizations.organization",
                            ),
                        ),
                        (
                            "user",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="organization_memberships",
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                    ],
                    options={
                        "db_table": "workflows_organizationmembership",
                        "verbose_name": "Organization Membership",
                        "verbose_name_plural": "Organization Memberships",
                        "constraints": [
                            models.UniqueConstraint(
                                fields=("organization", "user"),
                                name="unique_organization_membership",
                            ),
                        ],
                    },
                ),
            ],
        ),
        migrations.RunPython(
            move_content_types,
            reverse_content_types,
        ),
    ]