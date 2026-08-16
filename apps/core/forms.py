from django import forms

from .models import ContactMessage


class PublicFormProtectionFieldsMixin:
    """Add fields used by the server-side public-form protection layer."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["website"] = forms.CharField(
            required=False,
            widget=forms.TextInput(
                attrs={
                    "tabindex": "-1",
                    "autocomplete": "off",
                    "aria-hidden": "true",
                }
            ),
        )
        self.fields["submission_token"] = forms.CharField(
            widget=forms.HiddenInput()
        )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("website"):
            raise forms.ValidationError(
                "We could not process this form. Please return and try again."
            )
        return cleaned_data


class ContactForm(PublicFormProtectionFieldsMixin, forms.ModelForm):

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
