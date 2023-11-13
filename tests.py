from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from django.urls import reverse
from leads.models import User, Lead, Agent


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

    def test_user_cant_login_with_wrong_username(self):
        response = self.client.post(
            reverse("login"),
            {"username": "wrongusername", "password": self.default_password},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password.")

    def test_user_cant_login_with_wrong_password(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.default_username, "password": "wrongpassword"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password.")

    def test_user_can_logout(self):
        self.client.login(
            username=self.default_username, password=self.default_password
        )
        response = self.client.get(reverse("logout"), follow=True)
        self.assertRedirects(response, reverse("landing-page"))


class FuntionalTest(StaticLiveServerTestCase):
    def setUp(self) -> None:
        options = Options()
        options.add_argument("--headless")
        self.browser = webdriver.Chrome(options=options)

        self.default_username = "testuser"
        self.default_password = "testpass"
        self.user = User.objects.create_user(
            username=self.default_username, password=self.default_password
        )

    def user_logs_in(self):
        self.browser.get(self.live_server_url + reverse("login"))
        self.browser.find_element(By.ID, "id_username").send_keys(self.default_username)
        self.browser.find_element(By.ID, "id_password").send_keys(self.default_password)
        self.browser.find_element(By.ID, "login").click()

    def tearDown(self) -> None:
        self.browser.close()


class TestLogingFlows(FuntionalTest):
    def test_user_logs_in(self):
        self.user_logs_in()
        self.assertEqual(
            self.browser.current_url, self.live_server_url + reverse("leads:lead-list")
        )

    def test_user_logs_out(self):
        self.user_logs_in()
        self.browser.find_element(By.ID, "logout").click()
        self.assertEqual(
            self.browser.current_url, self.live_server_url + reverse("landing-page")
        )


class TestLeadFlows(FuntionalTest):
    def test_user_creates_lead(self):
        self.user_logs_in()
        self.browser.find_element(By.ID, "create_lead").click()
        self.browser.find_element(By.ID, "id_first_name").send_keys("Test")
        self.browser.find_element(By.ID, "id_last_name").send_keys("Lead")
        self.browser.find_element(By.ID, "id_age").send_keys("30")
        self.browser.find_element(By.ID, "id_description").send_keys("A lead.")
        self.browser.find_element(By.ID, "id_phone_number").send_keys("123456789")
        self.browser.find_element(By.ID, "id_email").send_keys("testlead@leads.com")
        self.browser.find_element(By.ID, "create_lead").click()
        self.assertEqual(
            self.browser.current_url, self.live_server_url + reverse("leads:lead-list")
        )
        Lead.objects.get(first_name="Test", last_name="Lead")


class TestAgentFlows(FuntionalTest):
    def test_user_creates_agent(self):
        self.user_logs_in()
        self.browser.find_element(By.ID, "agents_list").click()
        self.browser.find_element(By.ID, "create_agent").click()
        self.browser.find_element(By.ID, "id_username").send_keys("testagent")
        self.browser.find_element(By.ID, "id_first_name").send_keys("Test")
        self.browser.find_element(By.ID, "id_last_name").send_keys("Agent")
        self.browser.find_element(By.ID, "create_agent").click()
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + reverse("agents:agent-list"),
        )
        agent = Agent.objects.get(user__username="testagent")
        try:
            self.browser.find_element(
                By.XPATH,
                f"//*[contains(text(), '{agent.user.first_name} {agent.user.last_name}')]",
            )
        except NoSuchElementException:
            self.fail("Agent not found on agents list.")
