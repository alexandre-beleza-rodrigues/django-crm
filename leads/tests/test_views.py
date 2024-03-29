from django.test import TestCase
from django.urls import reverse
from leads.models import User, Lead, Agent, Category
from leads.forms import (
    LeadModelForm,
    UserCreationForm,
    CategoryModelForm,
)
from leads.tests import ViewTestCase


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


class TestLeadListView(ViewTestCase):
    def test_correct_template_is_used(self):
        response = self.client.get(reverse("leads:lead-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/lead_list.html")

    def test_correct_leads_are_returned(self):
        initial_leads = list(Lead.objects.all())

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
        self.assertListEqual(
            list(response.context["leads"]), initial_leads + [lead_john, lead_jane]
        )

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

    def test_agent_only_sees_their_leads(self):
        username = "newagentuser"
        password = "testpass"

        agent_user = User.objects.create_user(
            username=username, password=password, is_organiser=False
        )
        agent = Agent.objects.create(
            user=agent_user, organisation=self.default_user.userprofile
        )

        self.default_lead.agent = agent
        self.default_lead.save()

        self.client.login(username=username, password=password)

        response = self.client.get(reverse("leads:lead-list"))
        self.assertListEqual(list(response.context["leads"]), [self.default_lead])

    def test_lead_list_page_loads_successfully_if_there_are_unassigned_leads(self):
        Lead.objects.create(
            first_name="John",
            last_name="Doe",
            age=33,
            organisation=self.default_user.userprofile,
        )

        response = self.client.get(reverse("leads:lead-list"))
        self.assertEqual(response.status_code, 200)

    def test_lead_list_contains_correct_unassigned_leads(self):
        Lead.objects.create(
            first_name="John",
            last_name="Doe",
            age=33,
            organisation=self.default_user.userprofile,
        )

        default_user_unassigned_leads = list(
            Lead.objects.filter(
                organisation=self.default_user.userprofile, agent__isnull=True
            )
        )

        other_user = User.objects.create_user(username="otheruser", password="testpass")
        Lead.objects.create(
            first_name="Jane",
            last_name="Doe",
            age=28,
            organisation=other_user.userprofile,
        )

        response = self.client.get(reverse("leads:lead-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["unassigned_leads"]), default_user_unassigned_leads
        )

    def test_only_authenticated_users_can_access_this_view(self):
        url = reverse("leads:lead-list")
        self.assert_only_authenticated_users_can_access_this_view(url)

    def test_unauthenticated_users_get_redirected_to_login(self):
        url = reverse("leads:lead-list")
        redirect_url = "/login/?next=/leads/"
        self.assert_unauthenticated_users_get_redirected_to(url, redirect_url)


class TestLeadDetailView(ViewTestCase):
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

    def test_correct_lead_is_returned_to_agent(self):
        username = "newagentuser"
        password = "testpass"

        agent_user = User.objects.create_user(
            username=username, password=password, is_organiser=False
        )
        agent = Agent.objects.create(
            user=agent_user, organisation=self.default_user.userprofile
        )

        lead = Lead.objects.create(
            first_name="John",
            last_name="Doe",
            organisation=self.default_user.userprofile,
            agent=agent,
        )

        self.client.login(username=username, password=password)

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
        url = reverse("leads:lead-detail", kwargs={"pk": self.default_lead.pk})
        self.assert_only_authenticated_users_can_access_this_view(url)

    def test_unauthenticated_users_get_redirected_to_login(self):
        url = reverse("leads:lead-detail", kwargs={"pk": self.default_lead.pk})
        redirect_url = f"/login/?next=/leads/{self.default_lead.pk}/"
        self.assert_unauthenticated_users_get_redirected_to(url, redirect_url)


class TestLeadCreateView(ViewTestCase):
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

    def test_form_only_accepts_agents_from_the_same_organisation(self):
        other_user = User.objects.create_user(username="otheruser", password="testpass")
        other_agent = Agent.objects.create(
            user=User.objects.create_user(username="otheragent", password="testpass"),
            organisation=other_user.userprofile,
        )

        response = self.client.get(reverse("leads:lead-create"))
        self.assertNotIn(other_agent, response.context["form"].fields["agent"].queryset)

    def test_only_authenticated_users_can_access_this_view(self):
        url = reverse("leads:lead-create")
        self.assert_only_authenticated_users_can_access_this_view(url)

    def test_unauthenticated_users_get_redirected_to_login(self):
        url = reverse("leads:lead-create")
        redirect_url = "/login/?next=/leads/"
        self.assert_unauthenticated_users_get_redirected_to(url, redirect_url)


class TestLeadUpdateView(ViewTestCase):
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

    def test_form_only_accepts_agents_from_the_same_organisation(self):
        other_user = User.objects.create_user(username="otheruser", password="testpass")
        other_agent = Agent.objects.create(
            user=User.objects.create_user(username="otheragent", password="testpass"),
            organisation=other_user.userprofile,
        )

        response = self.client.get(
            reverse("leads:lead-update", kwargs={"pk": self.default_lead.pk})
        )

        self.assertNotIn(other_agent, response.context["form"].fields["agent"].queryset)

    def test_only_authenticated_users_can_access_this_view(self):
        url = reverse("leads:lead-update", kwargs={"pk": self.default_lead.pk})
        self.assert_only_authenticated_users_can_access_this_view(url)

    def test_unauthenticated_users_get_redirected_to_login(self):
        url = reverse("leads:lead-update", kwargs={"pk": self.default_lead.pk})
        redirect_url = "/login/?next=/leads/"
        self.assert_unauthenticated_users_get_redirected_to(url, redirect_url)


class TestLeadDeleteView(ViewTestCase):
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
        url = reverse("leads:lead-delete", kwargs={"pk": self.default_lead.pk})
        self.assert_only_authenticated_users_can_access_this_view(url)

    def test_unauthenticated_users_get_redirected_to_login(self):
        url = reverse("leads:lead-delete", kwargs={"pk": self.default_lead.pk})
        redirect_url = "/login/?next=/leads/"
        self.assert_unauthenticated_users_get_redirected_to(url, redirect_url)


class TestCategoryListView(ViewTestCase):
    def test_correct_template_is_used(self):
        response = self.client.get(reverse("leads:category-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/category_list.html")

    def test_correct_list_is_returned(self):
        Category.objects.create(
            name="Contacted", organisation=self.default_user.userprofile
        )
        category_list = list(Category.objects.all())
        response = self.client.get(reverse("leads:category-list"))
        self.assertListEqual(list(response.context["categories"]), category_list)

    def test_correct_list_is_returned_to_agent(self):
        Category.objects.create(
            name="Contacted", organisation=self.default_user.userprofile
        )
        organization_categroy_list = list(
            Category.objects.filter(organisation=self.default_user.userprofile)
        )

        username = "newagentuser"
        password = "testpass"

        agent_user = User.objects.create_user(
            username=username, password=password, is_organiser=False
        )
        Agent.objects.create(
            user=agent_user, organisation=self.default_user.userprofile
        )

        self.client.login(username=username, password=password)

        response = self.client.get(reverse("leads:category-list"))
        self.assertListEqual(
            list(response.context["categories"]), organization_categroy_list
        )

    def test_only_authenticated_users_can_access_this_view(self):
        url = reverse("leads:category-list")
        self.assert_only_authenticated_users_can_access_this_view(url)

    def test_unauthenticated_users_get_redirected_to_login(self):
        url = reverse("leads:category-list")
        redirect_url = "/login/?next=/leads/categories/"
        self.assert_unauthenticated_users_get_redirected_to(url, redirect_url)


class TestCategoryDetailView(ViewTestCase):
    def test_correct_template_is_used(self):
        url = reverse("leads:category-detail", kwargs={"pk": self.default_category.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/category_detail.html")

    def test_correct_leads_are_returned(self):
        self.default_lead.category = self.default_category
        self.default_lead.save()
        lead_list = list(self.default_category.leads.all())

        url = reverse("leads:category-detail", kwargs={"pk": self.default_category.pk})
        response = self.client.get(url)
        self.assertListEqual(list(response.context["category"].leads.all()), lead_list)

    def test_correct_lead_is_returned_to_agent(self):
        username = "newagentuser"
        password = "testpass"

        agent_user = User.objects.create_user(
            username=username, password=password, is_organiser=False
        )
        Agent.objects.create(
            user=agent_user, organisation=self.default_user.userprofile
        )

        self.client.login(username=username, password=password)

        url = reverse("leads:category-detail", kwargs={"pk": self.default_category.pk})
        response = self.client.get(url)
        self.assertEqual(response.context["category"], self.default_category)

    def test_only_authenticated_users_can_access_this_view(self):
        url = reverse("leads:category-detail", kwargs={"pk": self.default_category.pk})
        self.assert_only_authenticated_users_can_access_this_view(url)

    def test_unauthenticated_users_get_redirected_to_login(self):
        url = reverse("leads:category-detail", kwargs={"pk": self.default_category.pk})
        redirect_url = f"/login/?next=/leads/categories/{self.default_category.pk}/"
        self.assert_unauthenticated_users_get_redirected_to(url, redirect_url)


class TestCategoryCreateView(ViewTestCase):
    def test_correct_template_is_used(self):
        response = self.client.get(reverse("leads:category-create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/category_create.html")

    def test_correct_form_is_used(self):
        response = self.client.get(reverse("leads:category-create"))
        self.assertIsInstance(response.context["form"], CategoryModelForm)

    def test_creates_new_category(self):
        initial_category_count = Category.objects.count()

        url = reverse("leads:category-create")
        data = {"name": "New Category"}
        self.client.post(url, data=data)

        try:
            Category.objects.get(name="New Category")
            self.assertEqual(Category.objects.count(), initial_category_count + 1)
        except Category.DoesNotExist:
            self.fail("Category was not created")

    def test_redirects_to_category_list_on_success(self):
        url = reverse("leads:category-create")
        data = {"name": "New Category"}
        response = self.client.post(url, data=data, follow=True)
        self.assertRedirects(response, reverse("leads:category-list"))

    def test_only_authenticated_users_can_access_this_view(self):
        url = reverse("leads:category-create")
        self.assert_only_authenticated_users_can_access_this_view(url)

    def test_unauthenticated_users_get_redirected_to_login(self):
        url = reverse("leads:category-create")
        redirect_url = "/login/?next=/leads/"
        self.assert_unauthenticated_users_get_redirected_to(url, redirect_url)


class TestCategoryUpdateView(ViewTestCase):
    def test_correct_template_is_used(self):
        url = reverse("leads:category-update", kwargs={"pk": self.default_category.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/category_update.html")

    def test_correct_form_is_used(self):
        url = reverse("leads:category-update", kwargs={"pk": self.default_category.pk})
        response = self.client.get(url)
        self.assertIsInstance(response.context["form"], CategoryModelForm)

    def test_valid_form_data_updates_category(self):
        url = reverse("leads:category-update", kwargs={"pk": self.default_category.pk})
        data = {"name": "New Category"}
        self.client.post(url, data=data, follow=True)
        self.default_category.refresh_from_db()
        self.assertEqual(self.default_category.name, "New Category")
        data = {"name": "Category"}
        self.client.post(url, data=data, follow=True)
        self.default_category.refresh_from_db()
        self.assertEqual(self.default_category.name, "Category")

    def test_invalid_form_data_does_not_update_category(self):
        url = reverse("leads:category-update", kwargs={"pk": self.default_category.pk})
        data = {"name": ""}
        self.client.post(url, data=data)
        self.default_category.refresh_from_db()
        self.assertNotEqual(self.default_category.name, "")

    def test_only_authenticated_users_can_access_this_view(self):
        url = reverse("leads:category-update", kwargs={"pk": self.default_category.pk})
        self.assert_only_authenticated_users_can_access_this_view(url)

    def test_unauthenticated_users_get_redirected_to_login(self):
        url = reverse("leads:category-update", kwargs={"pk": self.default_category.pk})
        redirect_url = "/login/?next=/leads/"
        self.assert_unauthenticated_users_get_redirected_to(url, redirect_url)


class TestCategoryDeleteView(ViewTestCase):
    def test_correct_template_is_used(self):
        url = reverse("leads:category-delete", kwargs={"pk": self.default_category.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/category_delete.html")

    def test_deletes_category(self):
        url = reverse("leads:category-delete", kwargs={"pk": self.default_category.pk})
        self.client.post(url, follow=True)
        self.assertNotIn(self.default_category, Category.objects.all())

    def test_redirects_to_category_list_on_success(self):
        url = reverse("leads:category-delete", kwargs={"pk": self.default_category.pk})
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse("leads:category-list"))

    def test_only_authenticated_users_can_access_this_view(self):
        url = reverse("leads:category-delete", kwargs={"pk": self.default_category.pk})
        self.assert_only_authenticated_users_can_access_this_view(url)

    def test_unauthenticated_users_get_redirected_to_login(self):
        url = reverse("leads:category-delete", kwargs={"pk": self.default_category.pk})
        redirect_url = "/login/?next=/leads/"
        self.assert_unauthenticated_users_get_redirected_to(url, redirect_url)
