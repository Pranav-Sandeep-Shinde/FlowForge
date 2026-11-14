import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Workflow(models.Model):
    """An editable workflow definition owned by an organization."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="workflows",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_workflows",
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Workflow"
        verbose_name_plural = "Workflows"

    def __str__(self):
        return self.name


class WorkflowNode(models.Model):
    """A configurable operation placed in a workflow definition."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name="nodes",
    )
    node_type = models.CharField(max_length=100)
    name = models.CharField(max_length=150)
    configuration = models.JSONField(default=dict, blank=True)
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)

    class Meta:
        ordering = ["name", "id"]
        verbose_name = "Workflow Node"
        verbose_name_plural = "Workflow Nodes"

    def clean(self):
        super().clean()
        if not isinstance(self.configuration, dict):
            raise ValidationError(
                {"configuration": "Node configuration must be a JSON object."}
            )

    def __str__(self):
        return f"{self.name} ({self.node_type})"


class WorkflowEdge(models.Model):
    """A directed connection between two nodes in a workflow."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_node = models.ForeignKey(
        WorkflowNode,
        on_delete=models.CASCADE,
        related_name="outgoing_edges",
    )
    target_node = models.ForeignKey(
        WorkflowNode,
        on_delete=models.CASCADE,
        related_name="incoming_edges",
    )
    source_handle = models.CharField(max_length=100, blank=True)
    target_handle = models.CharField(max_length=100, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(source_node=models.F("target_node")),
                name="workflow_edge_no_self_loop",
            ),
        ]
        verbose_name = "Workflow Edge"
        verbose_name_plural = "Workflow Edges"

    def clean(self):
        super().clean()
        if not self.source_node_id or not self.target_node_id:
            return

        if self.source_node_id == self.target_node_id:
            raise ValidationError({"target_node": "A node cannot connect to itself."})

        if self.source_node.workflow_id != self.target_node.workflow_id:
            raise ValidationError(
                {"target_node": "Both edge endpoints must belong to the same workflow."}
            )

    def __str__(self):
        return f"{self.source_node} -> {self.target_node}"
