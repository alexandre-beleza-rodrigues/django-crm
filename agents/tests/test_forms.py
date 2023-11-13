from django.test import TestCase
from agents.forms import AgentModelForm


class TestAgentModelForm(TestCase):
    def test_from_accepts_valid_data(self):
        form = AgentModelForm(
            {
                "username": "testagent",
                "first_name": "Test",
                "last_name": "Agent",
            }
        )
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_username(self):
        form = AgentModelForm(
            {
                "username": None,
                "first_name": "Test",
                "last_name": "Agent",
            }
        )
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_first_name(self):
        form = AgentModelForm(
            {
                "username": "testagent",
                "first_name": None,
                "last_name": "Agent",
            }
        )
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_last_name(self):
        form = AgentModelForm(
            {
                "username": "testagent",
                "first_name": "Test",
                "last_name": None,
            }
        )
        self.assertFalse(form.is_valid())
