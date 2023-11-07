from django.test import TestCase
from django.db.utils import IntegrityError
from leads.models import User, Lead


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
