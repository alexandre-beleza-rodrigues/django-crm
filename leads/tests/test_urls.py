from django.test import SimpleTestCase
from django.urls import reverse, resolve
from leads.views import (
    LeadListView,
    LeadDetailView,
)


class TestUrls(SimpleTestCase):
    def test_lead_list_url_resolves(self):
        url = reverse("leads:lead-list")
        self.assertEqual(resolve(url).func.view_class, LeadListView)

    def test_lead_detail_url_resolves(self):
        url = reverse("leads:lead-detail", args=[1])
        self.assertEqual(resolve(url).func.view_class, LeadDetailView)
