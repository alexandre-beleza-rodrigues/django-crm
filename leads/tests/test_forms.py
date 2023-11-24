from leads.tests import CRMTestCase
from leads.forms import LeadModelForm, UserCreationForm, CategoryModelForm
from leads.models import Agent, User, Category


class TestUserCreationForm(CRMTestCase):
    valid_form_data = {
        "username": "newuser",
        "password1": "v3rys3cur3pw",
        "password2": "v3rys3cur3pw",
    }

    def test_accepts_valid_data(self):
        form = UserCreationForm(self.valid_form_data)
        self.assertTrue(form.is_valid())

    def test_rejects_blank_username(self):
        data = self.valid_form_data.copy()
        data["username"] = None
        form = UserCreationForm(data)
        self.assertFalse(form.is_valid())

    def test_rejects_blank_password(self):
        data = self.valid_form_data.copy()
        data["password1"] = None
        data["password2"] = None
        form = UserCreationForm(data)
        self.assertFalse(form.is_valid())

    def test_rejects_not_matching_passwords(self):
        data = self.valid_form_data.copy()
        data["password1"] = "v3rys3cur3pw"
        data["password2"] = "notmatching"
        form = UserCreationForm(data)
        self.assertFalse(form.is_valid())


class TestLeadModelForm(CRMTestCase):
    def setUp(self):
        self.default_user = User.objects.create_user(
            username="testuser", password="testpass"
        )
        self.default_agent = Agent.objects.create(
            user=User.objects.create_user(username="testagen", password="testpass"),
            organisation=self.default_user.userprofile,
        )
        self.default_category = Category.objects.create(
            name="testcategory", organisation=self.default_user.userprofile
        )

    def test_from_accepts_valid_data(self):
        form = LeadModelForm(
            {
                "first_name": "Jony",
                "last_name": "Doe",
                "age": 25,
                "agent": self.default_agent,
                "category": self.default_category,
                "description": "John Doe's brother.",
                "phone_number": "123456789",
                "email": "jonydoe@does.com",
            }
        )
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_first_name(self):
        form = LeadModelForm(
            {
                "first_name": None,
                "last_name": "Doe",
                "age": 25,
                "agent": self.default_agent,
                "category": self.default_category,
                "description": "John Doe's brother.",
                "phone_number": "123456789",
                "email": "jonydoe@does.com",
            }
        )
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_last_name(self):
        form = LeadModelForm(
            {
                "first_name": "Jony",
                "last_name": None,
                "age": 25,
                "agent": self.default_agent,
                "category": self.default_category,
                "description": "John Doe's brother.",
                "phone_number": "123456789",
                "email": "jonydoe@does.com",
            }
        )
        self.assertFalse(form.is_valid())

    def test_form_rejects_word_for_age(self):
        form = LeadModelForm(
            {
                "first_name": "Jony",
                "last_name": "Doe",
                "age": "twenty-five",
                "agent": self.default_agent,
                "category": self.default_category,
                "description": "John Doe's brother.",
                "phone_number": "123456789",
                "email": "jonydoe@does.com",
            }
        )
        self.assertFalse(form.is_valid())

    def test_form_rejects_float_for_age(self):
        form = LeadModelForm(
            {
                "first_name": "Jony",
                "last_name": "Doe",
                "age": 25.7,
                "agent": self.default_agent,
                "category": self.default_category,
                "description": "John Doe's brother.",
                "phone_number": "123456789",
                "email": "jonydoe@does.com",
            }
        )
        self.assertFalse(form.is_valid())

    def test_form_allows_blank_age(self):
        form = LeadModelForm(
            {
                "first_name": "Jony",
                "last_name": "Doe",
                "age": None,
                "agent": self.default_agent,
                "category": self.default_category,
                "description": "John Doe's brother.",
                "phone_number": "123456789",
                "email": "jonydoe@does.com",
            }
        )
        self.assertTrue(form.is_valid())

    def test_form_rejects_negative_number_for_age(self):
        form = LeadModelForm(
            {
                "first_name": "Jony",
                "last_name": "Doe",
                "age": -25,
                "agent": self.default_agent,
                "category": self.default_category,
                "description": "John Doe's brother.",
                "phone_number": "123456789",
                "email": "jonydoe@does.com",
            }
        )
        self.assertFalse(form.is_valid())

    def test_form_rejects_string_for_agent(self):
        form = LeadModelForm(
            {
                "first_name": "Jony",
                "last_name": "Doe",
                "age": 25,
                "agent": "Jony's agent",
                "category": self.default_category,
                "description": "John Doe's brother.",
                "phone_number": "123456789",
                "email": "jonydoe@does.com",
            }
        )
        self.assertFalse(form.is_valid())

    def test_form_rejects_string_for_category(self):
        form = LeadModelForm(
            {
                "first_name": "Jony",
                "last_name": "Doe",
                "age": 25,
                "agent": self.default_agent,
                "category": "Jony's category",
                "description": "John Doe's brother.",
                "phone_number": "123456789",
                "email": "jonydoe@does.com",
            }
        )
        self.assertFalse(form.is_valid())

    def test_form_allows_blank_description(self):
        form = LeadModelForm(
            {
                "first_name": "Jony",
                "last_name": "Doe",
                "age": 25,
                "agent": self.default_agent,
                "category": self.default_category,
                "description": None,
                "phone_number": "123456789",
                "email": "jonydoe@does.com",
            }
        )
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_phone_number(self):
        form = LeadModelForm(
            {
                "first_name": "Jony",
                "last_name": "Doe",
                "age": 25,
                "agent": self.default_agent,
                "category": self.default_category,
                "description": "John Doe's brother.",
                "phone_number": None,
                "email": "jonydoe@does.com",
            }
        )
        self.assertFalse(form.is_valid())

    def test_form_rejects_invalid_email(self):
        form = LeadModelForm(
            {
                "first_name": "Jony",
                "last_name": "Doe",
                "age": 25,
                "agent": self.default_agent,
                "category": self.default_category,
                "description": "John Doe's brother.",
                "phone_number": "123456789",
                "email": "jonydoe",
            }
        )
        self.assertFalse(form.is_valid())


class TestCategoryModelForm(CRMTestCase):
    def test_form_accepts_valid_data(self):
        form = CategoryModelForm({"name": "testcategory"})
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_name(self):
        form = CategoryModelForm({"name": None})
        self.assertFalse(form.is_valid())
