from django.db import transaction

from modules.workflows.models import Workflow, WorkflowEdge, WorkflowNode


class WorkflowRepository:
    """Persistence operations for workflows and their editable graph."""

    def get_workflow(self, workflow_id):
        return Workflow.objects.get(pk=workflow_id)

    def list_workflows(self, organization_id):
        return Workflow.objects.filter(organization_id=organization_id)

    @transaction.atomic
    def add_node(
        self,
        workflow_id,
        *,
        node_type,
        name,
        configuration=None,
        position_x=0,
        position_y=0,
    ):
        workflow = Workflow.objects.get(pk=workflow_id)
        node = WorkflowNode(
            workflow=workflow,
            node_type=node_type,
            name=name,
            configuration={} if configuration is None else configuration,
            position_x=position_x,
            position_y=position_y,
        )
        node.full_clean()
        node.save()
        return node

    @transaction.atomic
    def add_edge(
        self,
        workflow_id,
        *,
        source_node_id,
        target_node_id,
        source_handle="",
        target_handle="",
    ):
        # Scoping both lookups ensures this repository cannot join nodes from
        # different workflows, even if the caller supplies unrelated IDs.
        source_node = WorkflowNode.objects.get(
            pk=source_node_id,
            workflow_id=workflow_id,
        )
        target_node = WorkflowNode.objects.get(
            pk=target_node_id,
            workflow_id=workflow_id,
        )
        edge = WorkflowEdge(
            source_node=source_node,
            target_node=target_node,
            source_handle=source_handle,
            target_handle=target_handle,
        )
        edge.full_clean()
        edge.save()
        return edge
