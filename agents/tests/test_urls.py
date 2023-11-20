from django.urls import reverse, resolve
from leads.tests import CRMTestCase
from agents.views import (
    AgentListView,
    AgentCreateView,
    AgentDetailView,
    AgentUpdateView,
    AgentDeleteView,
)


class TestUrls(CRMTestCase):
    def test_agent_list_url_resolves(self):
        url = reverse("agents:agent-list")
        self.assertEqual(resolve(url).func.view_class, AgentListView)

    def test_agent_create_url_resolves(self):
        url = reverse("agents:agent-create")
        self.assertEqual(resolve(url).func.view_class, AgentCreateView)

    def test_agent_detail_url_resolves(self):
        url = reverse("agents:agent-detail", args=[self.default_agent.pk])
        self.assertEqual(resolve(url).func.view_class, AgentDetailView)

    def test_agent_update_url_resolves(self):
        url = reverse("agents:agent-update", args=[self.default_agent.pk])
        self.assertEqual(resolve(url).func.view_class, AgentUpdateView)

    def test_agent_delete_url_resolves(self):
        url = reverse("agents:agent-delete", args=[self.default_agent.pk])
        self.assertEqual(resolve(url).func.view_class, AgentDeleteView)
