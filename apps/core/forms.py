from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):

    class Meta:

        model = ContactMessage

        fields = (
            "name",
            "email",
            "subject",
            "message",
        )

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "autocomplete": "name",
                    "placeholder": "Your full name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "autocomplete": "email",
                    "placeholder": "you@example.com",
                }
            ),
            "subject": forms.TextInput(
                attrs={"placeholder": "What can we help with?"}
            ),
            "message": forms.Textarea(
                attrs={
                    "rows": 7,
                    "placeholder": "Share the details of your question or request…",
                }
            )
        }
