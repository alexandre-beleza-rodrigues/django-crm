from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from django.urls import reverse
from leads.models import User


class TestLoginRequest(TestCase):
    def setUp(self):
        self.default_username = "testuser"
        self.default_password = "testpass"
        self.user = User.objects.create_user(
            username=self.default_username, password=self.default_password
        )

    def test_user_can_login(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.default_username, "password": self.default_password},
            follow=True,
        )
        self.assertRedirects(response, reverse("leads:lead-list"))


class FuntionalTest(StaticLiveServerTestCase):
    def setUp(self) -> None:
        options = Options()
        options.add_argument('--headless')
        self.browser = webdriver.Chrome(options=options)

    def tearDown(self) -> None:
        self.browser.close()


class TestLogin(FuntionalTest):
    def setUp(self) -> None:
        super().setUp()
        self.default_username = "testuser"
        self.default_password = "testpass"
        self.user = User.objects.create_user(
            username=self.default_username, password=self.default_password
        )

    def test_user_can_login(self):
        self.browser.get(self.live_server_url + reverse("login"))
        self.browser.find_element(By.ID, "id_username").send_keys(self.default_username)
        self.browser.find_element(By.ID, "id_password").send_keys(self.default_password)
        self.browser.find_element(By.ID, "login").click()
        self.assertEqual(
            self.browser.current_url, self.live_server_url + reverse("leads:lead-list")
        )
