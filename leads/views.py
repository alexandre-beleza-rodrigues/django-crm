from django.shortcuts import render
from .models import Lead
from .forms import LeadForm


def lead_list(request):
    _leads = Lead.objects.all()
    context = {"leads": _leads}
    return render(request, "lead_list.html", context)


def lead_detail(request, pk):
    _lead = Lead.objects.get(id=pk)
    context = {"lead": _lead}
    return render(request, "lead_detail.html", context)


def lead_create(request):
    context = {
        "form": LeadForm()
    }
    return render(request, "lead_create.html", context)
