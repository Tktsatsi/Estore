from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "title", "comment"]
        widgets = {
            "rating": forms.Select(
                choices=[
                    (i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)
                ],
                attrs={"class": "form-select"},
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Summary of your review",
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Tell us about your experience...",
                }
            ),
        }
        labels = {
            "rating": "Rating",
            "title": "Review Title",
            "comment": "Your Review",
        }
