from django import forms
from .models import Store, Product


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ["name", "slug", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter store name",
                }
            ),
            "slug": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "store-name"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Describe your store",
                }
            ),
        }
        help_texts = {
            "slug": "URL-friendly name (lowercase, no spaces, use hyphens)",
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "slug",
            "description",
            "category",
            "price",
            "stock",
            "image",
            "active",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Product name"}
            ),
            "slug": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "product-name"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Product description",
                }
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
            "stock": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "0"}
            ),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        help_texts = {
            "slug": "URL-friendly name (lowercase, no spaces, use hyphens)",
            "price": "Enter price in Rands (e.g., 999.99)",
        }
