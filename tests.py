from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from django.test import TestCase
from django.urls import reverse
from leads.models import User, Lead, Agent
from leads.tests import CRMStaticLiveServerTestCase


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


class FuntionalTest(CRMStaticLiveServerTestCase):
    def setUp(self) -> None:
        options = Options()
        options.add_argument("--headless")
        self.browser = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self) -> None:
        self.browser.close()

    def user_logs_in(self):
        self.browser.get(self.live_server_url + reverse("login"))
        self.browser.find_element(By.ID, "id_username").send_keys(self.default_username)
        self.browser.find_element(By.ID, "id_password").send_keys(self.default_password)
        self.browser.find_element(By.ID, "login").click()


class TestLoging(FuntionalTest):
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

    def test_login_button_disappears_after_login(self):
        self.user_logs_in()
        try:
            self.browser.find_element(By.XPATH, "//a[contains(text(), 'Login')]")
            self.fail("Login button found after login.")
        except NoSuchElementException:
            pass

    def test_login_page_redirects_to_landing_page_if_user_is_logged_in(self):
        self.user_logs_in()

        login_url = self.live_server_url + reverse("login")
        home_url = self.live_server_url + reverse("landing-page")

        self.browser.get(login_url)
        self.assertEqual(self.browser.current_url, home_url)

    def test_landing_page_does_not_containg_login_button_if_user_is_logged_in(self):
        self.user_logs_in()

        self.browser.get(self.live_server_url + reverse("landing-page"))

        try:
            self.browser.find_element(By.XPATH, "//a[contains(text(), 'Login')]")
            self.fail("Login button found after login.")
        except NoSuchElementException:
            pass


class TestLeads(FuntionalTest):
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
        Lead.objects.get(first_name="Test", last_name="Lead", age=30)

    def test_update_form_contains_current_values(self):
        self.user_logs_in()

        self.browser.get(
            self.live_server_url
            + reverse("leads:lead-update", args=[self.default_lead.pk])
        )

        self.assertEqual(
            self.browser.find_element(By.NAME, "first_name").get_attribute("value"),
            self.default_lead.first_name,
        )
        self.assertEqual(
            self.browser.find_element(By.NAME, "last_name").get_attribute("value"),
            self.default_lead.last_name,
        )
        self.assertEqual(
            self.browser.find_element(By.NAME, "age").get_attribute("value"),
            str(self.default_lead.age) if self.default_lead.age else "",
        )
        self.assertEqual(
            self.browser.find_element(By.NAME, "agent").get_attribute("value"),
            str(self.default_lead.agent.pk) if self.default_lead.agent else "",
        )
        self.assertEqual(
            self.browser.find_element(By.NAME, "category").get_attribute("value"),
            str(self.default_lead.category.pk) if self.default_lead.category else "",
        )
        self.assertEqual(
            self.browser.find_element(By.NAME, "description").get_attribute("value"),
            self.default_lead.description if self.default_lead.description else "",
        )
        self.assertEqual(
            self.browser.find_element(By.NAME, "phone_number").get_attribute("value"),
            self.default_lead.phone_number,
        )
        self.assertEqual(
            self.browser.find_element(By.NAME, "email").get_attribute("value"),
            self.default_lead.email,
        )

    def test_lead_list_contains_unassigned_leads(self):
        uniquely_named_lead = Lead.objects.create(
            first_name="Unassigned",
            last_name="Lead",
            age=30,
            phone_number="123456789",
            email="unassigned@leads.com",
            organisation=self.default_user.userprofile,
        )

        self.assertEqual(Lead.objects.filter(first_name="Unassigned").count(), 1)

        self.user_logs_in()

        self.browser.get(self.live_server_url + reverse("leads:lead-list"))

        try:
            self.browser.find_element(
                By.XPATH,
                "//*[contains("
                f"text(), '{uniquely_named_lead.first_name} {uniquely_named_lead.last_name}'"
                ")]",
            )
        except NoSuchElementException:
            self.fail("Unassigned lead not found on leads list.")

    def test_lead_view_categories_button_exists_in_lead_list(self):
        self.user_logs_in()
        self.browser.get(self.live_server_url + reverse("leads:lead-list"))
        view_categories_button = self.browser.find_element(By.ID, "view-categories")
        view_categories_button.click()
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + reverse("leads:category-list"),
        )


class TestAgents(FuntionalTest):
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

    def test_user_updates_agent(self):
        initial_agent_first_name = self.default_agent.user.first_name
        self.user_logs_in()
        self.browser.find_element(By.ID, "agents_list").click()
        agent_full_name_td = self.browser.find_element(
            By.XPATH,
            f"//*[contains(text(), "
            f"'{self.default_agent.user.first_name} {self.default_agent.user.last_name}')]",
        )
        agent_tr = agent_full_name_td.find_element(By.XPATH, "..")
        agent_tr.find_element(By.XPATH, "//a[contains(text(), 'Edit')]").click()
        self.browser.find_element(By.ID, "id_username").clear()
        self.browser.find_element(By.ID, "id_username").send_keys("updatedagent")
        self.browser.find_element(By.ID, "id_first_name").clear()
        self.browser.find_element(By.ID, "id_first_name").send_keys("Updated")
        self.browser.find_element(By.ID, "id_last_name").clear()
        self.browser.find_element(By.ID, "id_last_name").send_keys("Agent")
        self.browser.find_element(By.ID, "update_agent").click()
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url
            + reverse("agents:agent-detail", args=[self.default_agent.pk]),
        )
        self.default_agent.refresh_from_db()
        self.assertNotEqual(
            self.default_agent.user.first_name, initial_agent_first_name
        )
        self.assertEqual(self.default_agent.user.first_name, "Updated")
        try:
            self.browser.find_element(
                By.XPATH,
                f"//*[contains(text(), "
                f"'{self.default_agent.user.first_name} {self.default_agent.user.last_name}')]",
            )
        except NoSuchElementException:
            self.fail("Updated agent not found on agents list.")

    def test_user_moves_from_update_view_to_detail_view(self):
        self.user_logs_in()
        self.browser.get(
            self.live_server_url
            + reverse("agents:agent-update", args=[self.default_agent.pk])
        )
        self.browser.find_element(By.ID, "overview").click()
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url
            + reverse("agents:agent-detail", args=[self.default_agent.pk]),
        )

    def test_update_form_contains_current_values(self):
        self.user_logs_in()

        self.browser.get(
            self.live_server_url
            + reverse("agents:agent-update", args=[self.default_agent.pk])
        )

        self.assertEqual(
            self.browser.find_element(By.NAME, "email").get_attribute("value"),
            self.default_agent.user.email,
        )
        self.assertEqual(
            self.browser.find_element(By.NAME, "username").get_attribute("value"),
            self.default_agent.user.username,
        )
        self.assertEqual(
            self.browser.find_element(By.NAME, "first_name").get_attribute("value"),
            self.default_agent.user.first_name,
        )
        self.assertEqual(
            self.browser.find_element(By.NAME, "last_name").get_attribute("value"),
            self.default_agent.user.last_name,
        )


class TestArbitaryFlows(FuntionalTest):
    def test_user_creates_account_and_logs_in(self):
        username = "newuser"
        password = "v3rys3cur3pwd"

        # Create account
        self.browser.get(self.live_server_url + reverse("signup"))
        self.browser.find_element(By.ID, "id_username").send_keys(username)
        self.browser.find_element(By.ID, "id_password1").send_keys(password)
        self.browser.find_element(By.ID, "id_password2").send_keys(password)
        self.browser.find_element(By.ID, "signup").click()

        # Log in
        self.browser.find_element(By.ID, "id_username").send_keys(username)
        self.browser.find_element(By.ID, "id_password").send_keys(password)
        self.browser.find_element(By.ID, "login").click()

        # Check if logged in
        expected_url = self.live_server_url + reverse("leads:lead-list")
        self.assertEqual(self.browser.current_url, expected_url)

    def test_clicking_navbar_logo_app_name_redirect_to_landing_page(self):
        self.user_logs_in()

        self.browser.get(self.live_server_url + reverse("leads:lead-list"))
        self.browser.find_element(By.ID, "logo_app_name").click()

        self.assertEqual(
            self.browser.current_url, self.live_server_url + reverse("landing-page")
        )
