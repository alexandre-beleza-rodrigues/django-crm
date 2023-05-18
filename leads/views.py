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

from .forms import LeadModelForm
from .models import Lead


class LandingPageView(TemplateView):
    template_name = "landing.html"


class LeadListView(ListView):
    template_name = "leads/lead_list.html"
    queryset = Lead.objects.all()
    context_object_name = "leads"


class LeadDetailView(DetailView):
    template_name = "leads/lead_detail.html"
    queryset = Lead.objects.all()
    context_object_name = "lead"


class LeadCreateView(CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm

    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        send_mail(
            subject="A lead has been created.",
            message="Go to the site to see the new lead.",
            from_email="djcrm@djcrm.com",
            recipient_list=["general@djcrm.com"],
        )
        return super(LeadCreateView, self).form_valid(form)


class LeadUpdateView(UpdateView):
    template_name = "leads/lead_update.html"
    queryset = Lead.objects.all()
    form_class = LeadModelForm
    context_object_name = "lead"

    def get_success_url(self):
        return reverse("leads:lead-list")


class LeadDeleteView(DeleteView):
    template_name = "leads/lead_delete.html"
    queryset = Lead.objects.all()
    context_object_name = "lead"

    def get_success_url(self):
        return reverse("leads:lead-list")
