from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    account_type = forms.ChoiceField(
        choices=[
            ("buyer", "Buyer - I want to shop"),
            ("vendor", "Vendor - I want to sell"),
        ],
        widget=forms.RadioSelect,
        required=True,
        label="Account Type",
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
            "account_type",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            # Update profile based on account type
            profile = user.profile
            if self.cleaned_data["account_type"] == "vendor":
                profile.is_seller = True
                profile.is_buyer = True  # Vendors can also buy
            else:
                profile.is_seller = False
                profile.is_buyer = True
            profile.save()
        return user
