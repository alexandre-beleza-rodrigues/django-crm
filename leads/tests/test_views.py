from django.test import TestCase
from django.urls import reverse
from leads.models import User, Lead, Agent
from leads.forms import LeadModelForm, UserCreationForm
from leads.tests import CRMTestCase


class SignupViewTestCase(TestCase):
    def test_correct_template_is_used(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup.html")

    def test_correct_form_is_used(self):
        response = self.client.get(reverse("signup"))
        self.assertIsInstance(response.context["form"], UserCreationForm)

    def test_redirects_to_login_on_success(self):
        data = {
            "username": "testuser",
            "password1": "verysecurepassword",
            "password2": "verysecurepassword",
        }
        response = self.client.post(reverse("signup"), data=data, follow=True)
        self.assertRedirects(response, reverse("login"))


class LandingPageViewTestCase(TestCase):
    def test_correct_template_is_used(self):
        response = self.client.get(reverse("landing-page"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "landing.html")


class LeadViewTestCase(CRMTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(
            username=self.default_username, password=self.default_password
        )


class TestLeadListView(LeadViewTestCase):
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


class TestLeadDetailView(LeadViewTestCase):
    def test_correct_template_is_used(self):
        lead = Lead.objects.create(
            first_name="John",
            last_name="Doe",
            organisation=self.default_user.userprofile,
        )

        response = self.client.get(reverse("leads:lead-detail", kwargs={"pk": lead.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/lead_detail.html")

    def test_correct_lead_is_returned(self):
        lead = Lead.objects.create(
            first_name="John",
            last_name="Doe",
            organisation=self.default_user.userprofile,
        )

        response = self.client.get(reverse("leads:lead-detail", kwargs={"pk": lead.pk}))
        self.assertEqual(response.context["lead"], lead)

    def test_only_leads_in_same_organisation_can_be_accessed(self):
        other_user = User.objects.create_user(username="otheruser", password="testpass")

        Lead.objects.create(
            first_name="John",
            last_name="Doe",
            organisation=self.default_user.userprofile,
        )
        other_lead = Lead.objects.create(
            first_name="Jane",
            last_name="Doe",
            organisation=other_user.userprofile,
        )

        response = self.client.get(
            reverse("leads:lead-detail", kwargs={"pk": other_lead.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_only_authenticated_users_can_access_this_view(self):
        self.client.logout()

        lead = Lead.objects.create(
            first_name="John",
            last_name="Doe",
            organisation=self.default_user.userprofile,
        )

        response = self.client.get(reverse("leads:lead-detail", kwargs={"pk": lead.pk}))
        self.assertEqual(response.status_code, 302)

    def test_unauthenticated_users_get_redirected_to_login(self):
        self.client.logout()

        lead = Lead.objects.create(
            first_name="John",
            last_name="Doe",
            organisation=self.default_user.userprofile,
        )

        response = self.client.get(
            reverse("leads:lead-detail", kwargs={"pk": lead.pk}), follow=True
        )
        self.assertRedirects(response, "/login/?next=/leads/1/")


class TestLeadCreateView(LeadViewTestCase):
    def test_correct_template_is_used(self):
        response = self.client.get(reverse("leads:lead-create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/lead_create.html")

    def test_correct_form_is_used(self):
        response = self.client.get(reverse("leads:lead-create"))
        self.assertIsInstance(response.context["form"], LeadModelForm)

    def test_valid_form_data_creates_new_lead(self):
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "age": 33,
            "agent": self.default_agent.pk,
            "description": "Some description",
            "phone_number": "123456789",
            "email": "john@does.com",
        }

        initial_lead_count = Lead.objects.count()
        response = self.client.post(
            reverse("leads:lead-create"), data=data, follow=True
        )
        self.assertRedirects(response, reverse("leads:lead-list"))
        self.assertEqual(Lead.objects.count(), initial_lead_count + 1)

    def test_invalid_form_data_does_not_create_new_lead(self):
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "age": 33,
            "agent": self.default_agent.pk,
            "description": "Some description",
            "phone_number": "123456789",
            "email": "invalid_email",
        }

        initial_lead_count = Lead.objects.count()
        response = self.client.post(reverse("leads:lead-create"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lead.objects.count(), initial_lead_count)

    def test_missing_form_data_does_not_create_new_lead(self):
        data = {
            "first_name": "John",
            "last_name": "Doe",
        }

        initial_lead_count = Lead.objects.count()
        response = self.client.post(reverse("leads:lead-create"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lead.objects.count(), initial_lead_count)

    def test_only_authenticated_users_can_access_this_view(self):
        self.client.logout()
        response = self.client.get(reverse("leads:lead-create"))
        self.assertEqual(response.status_code, 302)

    def test_unauthenticated_users_get_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("leads:lead-create"), follow=True)
        self.assertRedirects(response, "/login/?next=/leads/")


class TestLeadUpdateView(LeadViewTestCase):
    def setUp(self):
        super().setUp()
        self.default_lead = Lead.objects.create(
            first_name="John",
            last_name="Doe",
            age=33,
            organisation=self.default_user.userprofile,
            description="Some description",
            phone_number="123456789",
            email="john@does.com",
        )

    def test_correct_template_is_used(self):
        lead = Lead.objects.create(
            first_name="John",
            last_name="Doe",
            organisation=self.default_user.userprofile,
        )

        response = self.client.get(reverse("leads:lead-update", kwargs={"pk": lead.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/lead_update.html")

    def test_correct_form_is_used(self):
        lead = Lead.objects.create(
            first_name="John",
            last_name="Doe",
            organisation=self.default_user.userprofile,
        )

        response = self.client.get(reverse("leads:lead-update", kwargs={"pk": lead.pk}))
        self.assertIsInstance(response.context["form"], LeadModelForm)

    def test_valid_form_data_updates_lead(self):
        lead = Lead.objects.create(
            first_name="John",
            last_name="Doe",
            age=33,
            organisation=self.default_user.userprofile,
            description="Some description",
            phone_number="123456789",
            email="help@does.com",
        )

        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "age": 33,
            "description": "Some description",
            "phone_number": "123456789",
            "email": "help@does.com",
        }

        response = self.client.post(
            reverse("leads:lead-update", kwargs={"pk": lead.pk}), data=data, follow=True
        )
        self.assertRedirects(
            response, reverse("leads:lead-detail", kwargs={"pk": lead.pk})
        )
        lead.refresh_from_db()
        self.assertEqual(lead.first_name, "Jane")

    def test_invalid_form_data_does_not_update_lead(self):
        lead = Lead.objects.create(
            first_name="John",
            last_name="Doe",
            age=33,
            organisation=self.default_user.userprofile,
            description="Some description",
            phone_number="123456789",
            email="help@does.com",
        )

        data = {
            "first_name": "John",
            "last_name": "Doe",
            "age": 33,
            "description": "Some description",
            "phone_number": "123456789",
            "email": "not_an_email",
        }

        response = self.client.post(
            reverse("leads:lead-update", kwargs={"pk": lead.pk}), data=data
        )
        self.assertEqual(response.status_code, 200)
        lead.refresh_from_db()
        self.assertEqual(lead.email, "help@does.com")

    def test_only_authenticated_users_can_access_this_view(self):
        self.client.logout()
        response = self.client.get(
            reverse("leads:lead-update", kwargs={"pk": self.default_lead.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_unauthenticated_users_get_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(
            reverse("leads:lead-update", kwargs={"pk": self.default_lead.pk}),
            follow=True,
        )
        self.assertRedirects(response, "/login/?next=/leads/")


class TestLeadDeleteView(LeadViewTestCase):
    def setUp(self):
        super().setUp()
        self.default_lead = Lead.objects.create(
            first_name="John",
            last_name="Doe",
            age=33,
            organisation=self.default_user.userprofile,
            description="Some description",
            phone_number="123456789",
            email="john@does.com",
        )

    def test_correct_template_is_used(self):
        response = self.client.get(
            reverse("leads:lead-delete", kwargs={"pk": self.default_lead.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/lead_delete.html")

    def test_deletes_lead(self):
        initial_lead_count = Lead.objects.count()
        response = self.client.post(
            reverse("leads:lead-delete", kwargs={"pk": self.default_lead.pk}),
            follow=True,
        )
        self.assertRedirects(response, reverse("leads:lead-list"))
        self.assertEqual(Lead.objects.count(), initial_lead_count - 1)

    def test_only_authenticated_users_can_access_this_view(self):
        self.client.logout()
        response = self.client.get(
            reverse("leads:lead-delete", kwargs={"pk": self.default_lead.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_unauthenticated_users_get_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(
            reverse("leads:lead-delete", kwargs={"pk": self.default_lead.pk}),
            follow=True,
        )
        self.assertRedirects(response, "/login/?next=/leads/")
