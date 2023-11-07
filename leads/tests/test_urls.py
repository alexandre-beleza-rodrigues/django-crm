from django.test import SimpleTestCase
from django.urls import reverse, resolve
from leads.views import (
    LeadListView,
    LeadDetailView,
    LeadCreateView,
    LeadUpdateView,
    LeadDeleteView,
)


class TestUrls(SimpleTestCase):
    def test_lead_list_url_resolves(self):
        url = reverse("leads:lead-list")
        self.assertEqual(resolve(url).func.view_class, LeadListView)

    def test_lead_detail_url_resolves(self):
        url = reverse("leads:lead-detail", args=[1])
        self.assertEqual(resolve(url).func.view_class, LeadDetailView)

    def test_lead_create_url_resolves(self):
        url = reverse("leads:lead-create")
        self.assertEqual(resolve(url).func.view_class, LeadCreateView)

    def test_lead_update_url_resolves(self):
        url = reverse("leads:lead-update", args=[1])
        self.assertEqual(resolve(url).func.view_class, LeadUpdateView)

    def test_lead_delete_url_resolves(self):
        url = reverse("leads:lead-delete", args=[1])
        self.assertEqual(resolve(url).func.view_class, LeadDeleteView)
