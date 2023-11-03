from django.test import TestCase
from django.urls import reverse
from leads.models import User


class TestLogin(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpass"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )

    def test_user_can_login(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.username, "password": self.password},
            follow=True,
        )
        self.assertRedirects(response, reverse("leads:lead-list"))
