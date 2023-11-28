from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from leads.models import User, Agent, Lead, Category


class CRMTestCase(TestCase):
    def setUp(self) -> None:
        self.default_username = "testuser"
        self.default_password = "testpass"
        self.default_user = User.objects.create_user(
            username=self.default_username, password=self.default_password
        )
        self.default_agent = Agent.objects.create(
            user=User.objects.create_user(username="agentuser", password="testpass"),
            organisation=self.default_user.userprofile,
        )
        self.default_lead = Lead.objects.create(
            first_name="Test",
            last_name="Lead",
            age=42,
            organisation=self.default_user.userprofile,
            agent=self.default_agent,
        )
        self.default_category = Category.objects.create(
            name="New", organisation=self.default_user.userprofile
        )


class CRMStaticLiveServerTestCase(StaticLiveServerTestCase):
    def setUp(self) -> None:
        self.default_username = "testuser"
        self.default_password = "testpass"
        self.default_user = User.objects.create_user(
            username=self.default_username, password=self.default_password
        )
        self.default_agent = Agent.objects.create(
            user=User.objects.create_user(username="agentuser", password="testpass"),
            organisation=self.default_user.userprofile,
        )
        self.default_lead = Lead.objects.create(
            first_name="Test",
            last_name="Lead",
            age=42,
            organisation=self.default_user.userprofile,
            agent=self.default_agent,
        )
        self.default_category = Category.objects.create(
            name="New", organisation=self.default_user.userprofile
        )


class ViewTestCase(CRMTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(
            username=self.default_username, password=self.default_password
        )

    def assert_only_authenticated_users_can_access_this_view(self, url):
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def assert_unauthenticated_users_get_redirected_to(self, url, redirect_url):
        self.client.logout()
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, redirect_url)
