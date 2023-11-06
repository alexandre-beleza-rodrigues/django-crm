from django.test import TestCase
from django.urls import reverse
from leads.models import User, Lead, Agent


class TestLeadListView(TestCase):
    def setUp(self):
        self.default_username = "testuser"
        self.default_password = "testpass"
        self.default_user = User.objects.create_user(
            username=self.default_username, password=self.default_password
        )
        self.default_agent = Agent.objects.create(
            user=User.objects.create_user(username="agentuser", password="testpass"),
            organisation=self.default_user.userprofile,
        )

        self.client.login(
            username=self.default_username, password=self.default_password
        )

    def test_correct_template_is_used(self):
        response = self.client.get(reverse("leads:lead-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/lead_list.html")

    def test_correct_leads_are_returned(self):
        lead_john = Lead.objects.create(
            first_name="John",
            last_name="Doe",
            age=33,
            organisation=self.default_user.userprofile,
            agent=self.default_agent,
        )
        lead_jane = Lead.objects.create(
            first_name="Jane",
            last_name="Doe",
            age=28,
            organisation=self.default_user.userprofile,
            agent=self.default_agent,
        )

        response = self.client.get(reverse("leads:lead-list"))
        self.assertListEqual(list(response.context["leads"]), [lead_john, lead_jane])

    def test_only_leads_in_same_organisation_can_be_accessed(self):
        other_user = User.objects.create_user(username="otheruser", password="testpass")
        other_agent = Agent.objects.create(
            user=User.objects.create_user(username="otheragent", password="testpass"),
            organisation=other_user.userprofile,
        )

        Lead.objects.create(
            first_name="John",
            last_name="Doe",
            age=33,
            organisation=self.default_user.userprofile,
            agent=self.default_agent,
        )
        lead_jane = Lead.objects.create(
            first_name="Jane",
            last_name="Doe",
            age=28,
            organisation=other_user.userprofile,
            agent=other_agent,
        )

        self.client.login(username="otheruser", password="testpass")
        response = self.client.get(reverse("leads:lead-list"))
        self.assertListEqual(list(response.context["leads"]), [lead_jane])

    def test_only_authenticated_users_can_access_this_view(self):
        self.client.logout()
        response = self.client.get(reverse("leads:lead-list"))
        self.assertEqual(response.status_code, 302)

    def test_unauthenticated_users_get_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("leads:lead-list"), follow=True)
        self.assertRedirects(response, "/login/?next=/leads/")
