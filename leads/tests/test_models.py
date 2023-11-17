from django.test import TestCase
from django.db.utils import IntegrityError
from leads.models import User, Lead, UserProfile, Agent
from leads.tests import CRMTestCase


class TestUserModel(TestCase):
    def test_str_representation(self):
        user = User.objects.create_user(username="testuser", password="testpass")
        self.assertEqual(str(user), "testuser")

    def test_user_create(self):
        initial_count = User.objects.count()
        User.objects.create_user(username="newtestuser", password="testpass")
        self.assertEqual(User.objects.count(), initial_count + 1)
        try:
            User.objects.get(username="newtestuser")
        except User.DoesNotExist:
            self.fail("User not created.")

    def test_user_update(self):
        user = User.objects.create_user(username="testuser", password="testpass")
        user.username = "newtestuser"
        user.save()
        self.assertEqual(user.username, "newtestuser")

    def test_user_delete(self):
        new_user = User.objects.create_user(username="newtestuser", password="testpass")
        initial_count = User.objects.count()
        new_user.delete()
        self.assertEqual(User.objects.count(), initial_count - 1)
        try:
            User.objects.get(username="newtestuser")
            self.fail("User not deleted.")
        except User.DoesNotExist:
            pass

    def test_is_organiser_should_be_true_by_default(self):
        user = User.objects.create_user(username="testuser", password="testpass")
        self.assertEqual(user.is_organiser, True)

    def test_is_agent_should_be_false_by_default(self):
        user = User.objects.create_user(username="testuser", password="testpass")
        self.assertEqual(user.is_agent, False)

    def test_is_organiser_should_be_mandatory(self):
        user = User.objects.create_user(username="testuser", password="testpass")
        with self.assertRaises(IntegrityError):
            user.is_organiser = None
            user.save()

    def test_is_agent_should_be_mandatory(self):
        user = User.objects.create_user(username="testuser", password="testpass")
        with self.assertRaises(IntegrityError):
            user.is_agent = None
            user.save()


class TestUserProfileModel(TestCase):
    def setUp(self) -> None:
        self.default_user = User.objects.create_user(
            username="testuser", password="testpass"
        )

    def test_str_representation(self):
        user_profile = UserProfile.objects.get(user=self.default_user)
        self.assertEqual(str(user_profile), self.default_user.username)

    def test_user_profile_create(self):
        initial_count = UserProfile.objects.count()
        user = User.objects.create_user(username="newtestuser", password="testpass")
        self.assertEqual(UserProfile.objects.count(), initial_count + 1)
        try:
            UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            self.fail("User profile not created.")

    def test_user_profile_update(self):
        user_profile = UserProfile.objects.get(user=self.default_user)
        user_profile.user.username = "newtestuser"
        user_profile.user.save()
        self.assertEqual(user_profile.user.username, "newtestuser")

    def test_user_profile_delete(self):
        new_user = User.objects.create_user(username="newtestuser", password="testpass")
        initial_count = UserProfile.objects.count()
        new_user.delete()
        self.assertEqual(UserProfile.objects.count(), initial_count - 1)
        try:
            UserProfile.objects.get(user=new_user)
            self.fail("User profile not deleted.")
        except UserProfile.DoesNotExist:
            pass

    def test_user_profile_should_be_mandatory(self):
        user_profile = UserProfile.objects.get(user=self.default_user)
        with self.assertRaises(IntegrityError):
            user_profile.user = None
            user_profile.save()


class TestLeadModel(TestCase):
    def setUp(self) -> None:
        self.default_user = User.objects.create_user(
            username="testuser", password="testpass"
        )
        self.default_lead = Lead.objects.create(
            first_name="Jane",
            last_name="Doe",
            age=25,
            organisation=self.default_user.userprofile,
            agent=None,
            category=None,
            description="Jon Doe's sister.",
            phone_number="123456789",
            email="jane.doe@does.com",
        )

    def tets_str_representation(self):
        self.assertEqual(str(self.default_lead), "Jane Doe")

    def test_lead_create(self):
        initial_count = Lead.objects.count()
        Lead.objects.create(
            first_name="John",
            last_name="Doe",
            organisation=self.default_user.userprofile,
        )
        self.assertEqual(Lead.objects.count(), initial_count + 1)

    def test_lead_update(self):
        self.assertNotEqual(self.default_lead.first_name, "Jani")
        self.default_lead.first_name = "Jani"
        self.default_lead.save()
        self.assertEqual(self.default_lead.first_name, "Jani")

    def test_lead_delete(self):
        initial_count = Lead.objects.count()
        john_doe = Lead.objects.create(
            first_name="John",
            last_name="Doe",
            organisation=self.default_user.userprofile,
        )
        self.assertEqual(Lead.objects.count(), initial_count + 1)
        john_doe.delete()
        self.assertEqual(Lead.objects.count(), initial_count)

    def test_first_name_should_be_mandatory(self):
        with self.assertRaises(IntegrityError):
            self.default_lead.first_name = None
            self.default_lead.save()

    def test_last_name_should_be_mandatory(self):
        with self.assertRaises(IntegrityError):
            self.default_lead.last_name = None
            self.default_lead.save()

    def test_age_should_be_optional(self):
        self.default_lead.age = None
        self.default_lead.save()
        self.assertEqual(self.default_lead.age, None)

    def test_organisation_should_be_mandatory(self):
        with self.assertRaises(IntegrityError):
            self.default_lead.organisation = None
            self.default_lead.save()

    def test_agent_should_be_optional(self):
        self.default_lead.agent = None
        self.default_lead.save()
        self.assertEqual(self.default_lead.agent, None)

    def test_category_should_be_optional(self):
        self.default_lead.category = None
        self.default_lead.save()
        self.assertEqual(self.default_lead.category, None)

    def test_description_should_be_optional(self):
        self.default_lead.description = ""
        self.default_lead.save()
        self.assertEqual(self.default_lead.description, "")

    def test_date_added_should_be_auto_generated(self):
        john_doe = Lead.objects.create(
            first_name="John",
            last_name="Doe",
            organisation=self.default_user.userprofile,
        )
        self.assertNotEqual(john_doe.date_added, None)

    def test_phone_number_should_be_mandatory(self):
        with self.assertRaises(IntegrityError):
            self.default_lead.phone_number = None
            self.default_lead.save()

    def test_email_should_be_mandatory(self):
        with self.assertRaises(IntegrityError):
            self.default_lead.email = None
            self.default_lead.save()


class TestAgentModel(CRMTestCase):
    def test_str_representation(self):
        new_agent = Agent.objects.create(
            user=self.default_user,
            organisation=self.default_user.userprofile,
        )
        self.assertEqual(str(new_agent), self.default_user.username)

    def test_agent_create(self):
        initial_count = Agent.objects.count()
        Agent.objects.create(
            user=self.default_user,
            organisation=self.default_user.userprofile,
        )
        self.assertEqual(Agent.objects.count(), initial_count + 1)
        try:
            Agent.objects.get(user=self.default_user)
        except Agent.DoesNotExist:
            self.fail("Agent not created.")

    def test_agent_update(self):
        self.default_agent.user.username = "newtestuser"
        self.default_agent.user.save()
        self.assertEqual(self.default_agent.user.username, "newtestuser")

    def test_agent_delete(self):
        initial_count = Agent.objects.count()
        self.default_agent.delete()
        self.assertEqual(Agent.objects.count(), initial_count - 1)
        try:
            Agent.objects.get(user=self.default_user)
            self.fail("Agent not deleted.")
        except Agent.DoesNotExist:
            pass
