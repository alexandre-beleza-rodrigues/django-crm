import random
from typing import Any, Dict

from django.core.mail import send_mail
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from leads.models import Agent

from .forms import AgentModelForm
from .mixins import OrganisorAndLoginRequiredMixin


class AgentListView(OrganisorAndLoginRequiredMixin, ListView):
    template_name = "agents/agent_list.html"
    context_object_name = "agents"

    def get_queryset(self):
        organisation = self.request.user.userprofile
        return Agent.objects.filter(organisation=organisation)


class AgentCreateView(OrganisorAndLoginRequiredMixin, CreateView):
    template_name = "agents/agent_create.html"
    form_class = AgentModelForm

    def get_success_url(self):
        return reverse("agents:agent-list")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_agent = True
        user.is_organiser = False
        user.set_password(f"{random.randint(0, 1000000)}")
        user.save()
        Agent.objects.create(user=user, organisation=self.request.user.userprofile)
        send_mail(
            subject="You are invited to be an agent",
            message="You were added as an agent on DJCRM. Please come login to start working.",
            from_email="admin@test.com",
            recipient_list=[user.email],
        )
        return super().form_valid(form)


class AgentDetailView(OrganisorAndLoginRequiredMixin, DetailView):
    template_name = "agents/agent_detail.html"
    context_object_name = "agent"

    def get_queryset(self):
        organisation = self.request.user.userprofile
        return Agent.objects.filter(organisation=organisation)


class AgentUpdateView(OrganisorAndLoginRequiredMixin, UpdateView):
    template_name = "agents/agent_update.html"
    form_class = AgentModelForm
    queryset = Agent.objects.all()
    context_object_name = "user"

    def get_object(self, queryset=None) -> Any:
        agent = super().get_object(queryset=queryset)
        return agent.user

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["agent"] = Agent.objects.get(user=self.object)
        return context

    def get_success_url(self):
        agent = Agent.objects.get(user=self.object)
        return reverse("agents:agent-detail", kwargs={"pk": agent.pk})


class AgentDeleteView(OrganisorAndLoginRequiredMixin, DeleteView):
    template_name = "agents/agent_delete.html"
    queryset = Agent.objects.all()
    context_object_name = "agent"

    def get_success_url(self):
        return reverse("agents:agent-list")
