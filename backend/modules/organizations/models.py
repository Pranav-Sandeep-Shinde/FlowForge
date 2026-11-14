
from django.conf import settings
from django.db import models


class Organization(models.Model):
    """
    Represents a workspace in FlowForge.

    An organization owns workflows and provides the boundary
    for isolating data between different customers.
    """

    name = models.CharField(max_length=150)

    slug = models.SlugField(
        max_length=180,
        unique=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_organizations",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "workflows_organization"
        ordering = ["name"]
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return self.name


class OrganizationMembership(models.Model):
    """
    Represents a user's membership in an organization.
    """

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization_memberships",
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "workflows_organizationmembership"
        constraints = [
        models.UniqueConstraint(
            fields=["organization", "user"],
            name="unique_organization_membership",
        ),
    ]
        verbose_name = "Organization Membership"
        verbose_name_plural = "Organization Memberships"

    def __str__(self):
        return f"{self.user} - {self.organization} ({self.role})"
