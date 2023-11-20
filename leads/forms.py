from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UsernameField

from .models import Lead, Category

User = get_user_model()


class UserCreationForm(DjangoUserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
        field_classes = {"username": UsernameField}


class LeadModelForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = (
            "first_name",
            "last_name",
            "age",
            "agent",
            "category",
            "description",
            "phone_number",
            "email",
        )


class CategoryModelForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name",)
