from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from leads.models import User, Agent, Lead


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
