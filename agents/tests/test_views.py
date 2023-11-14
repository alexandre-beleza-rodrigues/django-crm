from django.urls import reverse
from leads.tests import CRMTestCase


class TestAgentUpdateView(CRMTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.login(
            username=self.default_username, password=self.default_password
        )

    def test_updates_agent(self):
        self.default_agent.user.first_name = "Not Updated"
        self.client.post(
            reverse("agents:agent-update", kwargs={"pk": self.default_agent.pk}),
            {
                "first_name": "Updated",
                "last_name": "Agent",
                "username": "updatedagent",
                "email": "agent@agents.com",
            },
        )
        self.default_agent.refresh_from_db()
        self.assertEqual(self.default_agent.user.first_name, "Updated")

    def test_redirects_to_agent_detail_view(self):
        response = self.client.post(
            reverse("agents:agent-update", kwargs={"pk": self.default_agent.pk}),
            {
                "first_name": "Updated",
                "last_name": "Agent",
                "username": "updatedagent",
                "email": "agent@agents.com",
            },
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("agents:agent-detail", kwargs={"pk": self.default_agent.pk}),
        )
