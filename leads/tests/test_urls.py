from django.urls import reverse, resolve
from leads.tests import CRMTestCase
from leads.views import (
    LeadListView,
    LeadDetailView,
    LeadCreateView,
    LeadUpdateView,
    LeadDeleteView,
    CategoryListView,
    CategoryCreateView,
    CategoryDetailView,
    CategoryUpdateView,
    CategoryDeleteView,
)


class TestUrls(CRMTestCase):
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

    def test_category_list_url_resolves(self):
        url = reverse("leads:category-list")
        self.assertEqual(resolve(url).func.view_class, CategoryListView)

    def test_category_create_url_resolves(self):
        url = reverse("leads:category-create")
        self.assertEqual(resolve(url).func.view_class, CategoryCreateView)

    def test_category_detail_url_resolves(self):
        url = reverse("leads:category-detail", args=[self.default_category.pk])
        self.assertEqual(resolve(url).func.view_class, CategoryDetailView)

    def test_category_update_url_resolves(self):
        url = reverse("leads:category-update", args=[self.default_category.pk])
        self.assertEqual(resolve(url).func.view_class, CategoryUpdateView)

    def test_category_delete_url_resolves(self):
        url = reverse("leads:category-delete", args=[self.default_category.pk])
        self.assertEqual(resolve(url).func.view_class, CategoryDeleteView)
