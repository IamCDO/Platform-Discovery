from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import BusinessApplication, BusinessCategory, Product


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class BusinessApplicationForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=BusinessCategory.objects.all(), label="Category of business")
    location = forms.CharField(label="Business location", widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Online or explicit physical location"}))
    matriculation_number = forms.CharField(label="Matriculation number")

    class Meta:
        model = BusinessApplication
        fields = [
            "business_name",
            "owner_name",
            "matriculation_number",
            "category",
            "location",
            "email",
            "phone_number",
            "description",
        ]
        labels = {
            "business_name": "Business name",
            "owner_name": "Owner's name",
            "email": "Email address",
            "phone_number": "Phone number",
            "description": "Business description",
        }
        widgets = {
            "business_name": forms.TextInput(attrs={"class": "form-control"}),
            "owner_name": forms.TextInput(attrs={"class": "form-control"}),
            "matriculation_number": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }


class ProductForm(forms.ModelForm):
    image_url = forms.URLField(required=False, widget=forms.URLInput(attrs={"class": "form-control", "placeholder": "https://example.com/product-image.jpg"}))

    class Meta:
        model = Product
        fields = ["name", "image_url", "description", "price", "discount_percent", "stock", "is_available"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "discount_percent": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 100}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "is_available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
