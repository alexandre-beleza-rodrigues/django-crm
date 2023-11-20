from django.urls import reverse
from leads.tests import ViewTestCase
from leads.models import Agent, User


class TestAgentListView(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.login(
            username=self.default_username, password=self.default_password
        )

    def test_correct_template_used(self):
        response = self.client.get(reverse("agents:agent-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "agents/agent_list.html")

    def test_lists_correct_agents(self):
        agents = Agent.objects.filter(organisation=self.default_user.userprofile)
        response = self.client.get(reverse("agents:agent-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["agents"]), list(agents))

    def test_only_lists_agents_in_organisation(self):
        default_user_agents = Agent.objects.filter(
            organisation=self.default_user.userprofile
        )
        other_user = User.objects.create_user(username="otheruser", password="testpass")
        Agent.objects.create(
            user=User.objects.create_user(username="otheragent", password="testpass"),
            organisation=other_user.userprofile,
        )

        response = self.client.get(reverse("agents:agent-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["agents"]), list(default_user_agents))

    def test_only_authenticated_users_can_access_this_view(self):
        self.client.logout()
        url = reverse("agents:agent-list")
        self.assert_only_authenticated_users_can_access_this_view(url)

    def test_unauthenticated_users_get_redirected_to_login(self):
        self.client.logout()
        url = reverse("agents:agent-list")
        redirect_url = "/login/?next=/leads/"
        self.assert_unauthenticated_users_get_redirected_to_login(url, redirect_url)


class TestAgentCreateView(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.login(
            username=self.default_username, password=self.default_password
        )

    def test_correct_template_used(self):
        response = self.client.get(reverse("agents:agent-create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "agents/agent_create.html")

    def test_creates_agent(self):
        initial_agents_count = Agent.objects.count()
        url = reverse("agents:agent-create")
        data = {
            "first_name": "New",
            "last_name": "Agent",
            "username": "newagent",
            "email": "newagent@agents.com",
        }
        self.client.post(url, data)
        self.assertEqual(Agent.objects.count(), initial_agents_count + 1)
        try:
            User.objects.get(username="newagent")
        except User.DoesNotExist:
            self.fail("User was not created")

    def test_redirects_to_agent_list_view(self):
        url = reverse("agents:agent-create")
        data = {
            "first_name": "New",
            "last_name": "Agent",
            "username": "newagent",
            "email": "newagent@agents.com",
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse("agents:agent-list"))

    def test_only_authenticated_users_can_access_this_view(self):
        self.client.logout()
        url = reverse("agents:agent-create")
        self.assert_only_authenticated_users_can_access_this_view(url)

    def test_unauthenticated_users_get_redirected_to_login(self):
        self.client.logout()
        url = reverse("agents:agent-create")
        redirect_url = "/login/?next=/leads/"
        self.assert_unauthenticated_users_get_redirected_to_login(url, redirect_url)


class TestAgentDetailView(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.login(
            username=self.default_username, password=self.default_password
        )

    def test_correct_template_used(self):
        response = self.client.get(
            reverse("agents:agent-detail", kwargs={"pk": self.default_agent.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "agents/agent_detail.html")

    def test_returns_correct_agent(self):
        response = self.client.get(
            reverse("agents:agent-detail", kwargs={"pk": self.default_agent.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["agent"], self.default_agent)

    def test_only_authenticated_users_can_access_this_view(self):
        self.client.logout()
        url = reverse("agents:agent-detail", kwargs={"pk": self.default_agent.pk})
        self.assert_only_authenticated_users_can_access_this_view(url)

    def test_unauthenticated_users_get_redirected_to_login(self):
        self.client.logout()
        url = reverse("agents:agent-detail", kwargs={"pk": self.default_agent.pk})
        redirect_url = "/login/?next=/leads/"
        self.assert_unauthenticated_users_get_redirected_to_login(url, redirect_url)


class TestAgentUpdateView(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.login(
            username=self.default_username, password=self.default_password
        )

    def test_correct_template_used(self):
        response = self.client.get(
            reverse("agents:agent-update", kwargs={"pk": self.default_agent.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "agents/agent_update.html")

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

    def test_only_authenticated_users_can_access_this_view(self):
        self.client.logout()
        url = reverse("agents:agent-update", kwargs={"pk": self.default_agent.pk})
        self.assert_only_authenticated_users_can_access_this_view(url)

    def test_unauthenticated_users_get_redirected_to_login(self):
        self.client.logout()
        url = reverse("agents:agent-update", kwargs={"pk": self.default_agent.pk})
        redirect_url = "/login/?next=/leads/"
        self.assert_unauthenticated_users_get_redirected_to_login(url, redirect_url)
