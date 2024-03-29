from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
import django.contrib.auth.views as auth_views
from django.shortcuts import redirect

from agents.mixins import OrganisorAndLoginRequiredMixin

from .forms import (
    CategoryModelForm,
    LeadModelForm,
    UserCreationForm,
)
from .models import Category, Lead, Agent


class SinupView(CreateView):
    template_name = "registration/signup.html"
    form_class = UserCreationForm

    def get_success_url(self):
        return reverse("login")


class LoginView(auth_views.LoginView):
    template_name = "registration/login.html"

    def get_success_url(self):
        return reverse("leads:lead-list")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("landing-page")
        return super().dispatch(request, *args, **kwargs)


class LandingPageView(TemplateView):
    template_name = "landing.html"


class LeadListView(LoginRequiredMixin, ListView):
    template_name = "leads/lead_list.html"
    context_object_name = "leads"

    def get_queryset(self):
        user = self.request.user
        if user.is_organiser:
            queryset = Lead.objects.filter(
                organisation=user.userprofile, agent__isnull=False
            )
        else:
            queryset = Lead.objects.filter(
                organisation=user.agent.organisation, agent__isnull=False
            )
            queryset = queryset.filter(agent__user=user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_organiser:
            queryset = Lead.objects.filter(
                organisation=user.userprofile, agent__isnull=True
            )
            context.update({"unassigned_leads": queryset})
        return context


class LeadDetailView(LoginRequiredMixin, DetailView):
    template_name = "leads/lead_detail.html"
    context_object_name = "lead"

    def get_queryset(self):
        user = self.request.user
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            queryset = queryset.filter(agent__user=user)
        return queryset


class LeadCreateView(OrganisorAndLoginRequiredMixin, CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["agent"].queryset = Agent.objects.filter(
            organisation=self.request.user.userprofile
        )
        return form

    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.organisation = self.request.user.userprofile
        lead.save()
        send_mail(
            subject="A lead has been created.",
            message="Go to the site to see the new lead.",
            from_email="djcrm@djcrm.com",
            recipient_list=["general@djcrm.com"],
        )
        return super().form_valid(form)


class LeadUpdateView(OrganisorAndLoginRequiredMixin, UpdateView):
    template_name = "leads/lead_update.html"
    form_class = LeadModelForm
    context_object_name = "lead"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["agent"].queryset = Agent.objects.filter(
            organisation=self.request.user.userprofile
        )
        return form

    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organisation=user.userprofile)

    def get_success_url(self):
        return reverse("leads:lead-detail", kwargs={"pk": self.object.pk})


class LeadDeleteView(OrganisorAndLoginRequiredMixin, DeleteView):
    template_name = "leads/lead_delete.html"
    context_object_name = "lead"

    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organisation=user.userprofile)

    def get_success_url(self):
        return reverse("leads:lead-list")


class CategoryListView(LoginRequiredMixin, ListView):
    template_name = "leads/category_list.html"
    context_object_name = "categories"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_organiser:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)

        context.update(
            {"unassigned_lead_count": queryset.filter(category__isnull=True).count()}
        )
        return context

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organiser:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
        return queryset


class CategoryDetailView(LoginRequiredMixin, DetailView):
    template_name = "leads/category_detail.html"
    context_object_name = "category"

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organiser:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
        return queryset


class CategoryCreateView(OrganisorAndLoginRequiredMixin, CreateView):
    template_name = "leads/category_create.html"
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse("leads:category-list")

    def form_valid(self, form):
        category = form.save(commit=False)
        category.organisation = self.request.user.userprofile
        category.save()
        return super().form_valid(form)


class CategoryUpdateView(OrganisorAndLoginRequiredMixin, UpdateView):
    template_name = "leads/category_update.html"
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse("leads:category-list")

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organiser:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
        return queryset


class CategoryDeleteView(OrganisorAndLoginRequiredMixin, DeleteView):
    template_name = "leads/category_delete.html"

    def get_success_url(self):
        return reverse("leads:category-list")

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organiser:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
        return queryset
