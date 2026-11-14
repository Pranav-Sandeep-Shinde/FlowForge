from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from modules.organizations.models import Organization
from modules.workflows.application.repositories import WorkflowRepository
from modules.workflows.models import Workflow, WorkflowEdge, WorkflowNode


class WorkflowModelTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Acme", slug="acme")

    def test_workflow_has_stable_identity_and_definition_metadata(self):
        workflow = Workflow.objects.create(
            organization=self.organization,
            name="Lead intake",
            description="Qualify incoming leads.",
        )

        self.assertEqual(workflow.organization, self.organization)
        self.assertEqual(workflow.name, "Lead intake")
        self.assertEqual(workflow.description, "Qualify incoming leads.")
        self.assertIsNone(workflow.created_by)
        self.assertIsNotNone(workflow.pk)
        self.assertIsNotNone(workflow.created_at)
        self.assertIsNotNone(workflow.updated_at)

    def test_same_name_is_allowed_in_another_organization(self):
        other_organization = Organization.objects.create(
            name="Other",
            slug="other",
        )

        first_workflow = Workflow.objects.create(
            organization=self.organization,
            name="Onboarding",
        )
        second_workflow = Workflow.objects.create(
            organization=other_organization,
            name="Onboarding",
        )

        self.assertNotEqual(first_workflow.pk, second_workflow.pk)

    def test_deleting_creator_preserves_workflow_and_clears_creator(self):
        user = get_user_model().objects.create_user(username="workflow-author")
        workflow = Workflow.objects.create(
            organization=self.organization,
            created_by=user,
            name="Lead intake",
        )

        user.delete()
        workflow.refresh_from_db()

        self.assertIsNone(workflow.created_by)

    def test_deleting_organization_deletes_its_workflows(self):
        workflow = Workflow.objects.create(
            organization=self.organization,
            name="Lead intake",
        )

        self.organization.delete()

        self.assertFalse(Workflow.objects.filter(pk=workflow.pk).exists())


class WorkflowGraphTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Acme", slug="acme")
        self.workflow = Workflow.objects.create(
            organization=self.organization,
            name="Lead intake",
        )
        self.other_workflow = Workflow.objects.create(
            organization=self.organization,
            name="Order processing",
        )
        self.repository = WorkflowRepository()

    def test_repository_creates_node_with_default_configuration_and_position(self):
        node = self.repository.add_node(
            self.workflow.pk,
            node_type="manual_trigger",
            name="Start",
        )

        self.assertEqual(node.workflow, self.workflow)
        self.assertEqual(node.configuration, {})
        self.assertEqual((node.position_x, node.position_y), (0, 0))

    def test_node_configuration_must_be_a_json_object(self):
        with self.assertRaises(ValidationError):
            self.repository.add_node(
                self.workflow.pk,
                node_type="manual_trigger",
                name="Start",
                configuration=["not", "an object"],
            )

    def test_repository_creates_directed_edge_between_workflow_nodes(self):
        source = self.repository.add_node(
            self.workflow.pk,
            node_type="manual_trigger",
            name="Start",
        )
        target = self.repository.add_node(
            self.workflow.pk,
            node_type="http_request",
            name="Fetch data",
        )

        edge = self.repository.add_edge(
            self.workflow.pk,
            source_node_id=source.pk,
            target_node_id=target.pk,
            source_handle="success",
            target_handle="input",
        )

        self.assertEqual(edge.source_node, source)
        self.assertEqual(edge.target_node, target)
        self.assertEqual(edge.source_handle, "success")
        self.assertEqual(edge.target_handle, "input")

    def test_repository_rejects_edge_endpoint_from_another_workflow(self):
        source = self.repository.add_node(
            self.workflow.pk,
            node_type="manual_trigger",
            name="Start",
        )
        target = self.repository.add_node(
            self.other_workflow.pk,
            node_type="http_request",
            name="Fetch data",
        )

        with self.assertRaises(WorkflowNode.DoesNotExist):
            self.repository.add_edge(
                self.workflow.pk,
                source_node_id=source.pk,
                target_node_id=target.pk,
            )

    def test_edge_model_validation_rejects_endpoints_from_different_workflows(self):
        source = self.repository.add_node(
            self.workflow.pk,
            node_type="manual_trigger",
            name="Start",
        )
        target = self.repository.add_node(
            self.other_workflow.pk,
            node_type="http_request",
            name="Fetch data",
        )
        edge = WorkflowEdge(source_node=source, target_node=target)

        with self.assertRaises(ValidationError):
            edge.full_clean()

    def test_edge_model_validation_rejects_self_connection(self):
        node = self.repository.add_node(
            self.workflow.pk,
            node_type="manual_trigger",
            name="Start",
        )
        edge = WorkflowEdge(source_node=node, target_node=node)

        with self.assertRaises(ValidationError):
            edge.full_clean()

    def test_database_rejects_self_connection(self):
        node = self.repository.add_node(
            self.workflow.pk,
            node_type="manual_trigger",
            name="Start",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                WorkflowEdge.objects.create(source_node=node, target_node=node)

    def test_deleting_node_deletes_its_edges(self):
        source = self.repository.add_node(
            self.workflow.pk,
            node_type="manual_trigger",
            name="Start",
        )
        target = self.repository.add_node(
            self.workflow.pk,
            node_type="http_request",
            name="Fetch data",
        )
        edge = self.repository.add_edge(
            self.workflow.pk,
            source_node_id=source.pk,
            target_node_id=target.pk,
        )

        source.delete()

        self.assertFalse(WorkflowEdge.objects.filter(pk=edge.pk).exists())

    def test_repository_reads_are_scoped_to_organization_and_workflow(self):
        self.assertEqual(
            list(self.repository.list_workflows(self.organization.pk)),
            [self.workflow, self.other_workflow],
        )
        self.assertEqual(
            self.repository.get_workflow(self.workflow.pk),
            self.workflow,
        )
