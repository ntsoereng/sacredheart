from datetime import date

from django import forms

from apps.core.forms import PublicFormProtectionFieldsMixin

from .models import AlumniOpportunity, AlumniStory, MentorshipRequest


class AlumniProfileUpdateVerificationForm(
    PublicFormProtectionFieldsMixin,
    forms.Form,
):
    email = forms.EmailField(
        label="Private email on the profile",
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "placeholder": "you@example.com",
            }
        ),
    )


class AlumniProfileUpdateRequestForm(
    PublicFormProtectionFieldsMixin,
    forms.Form,
):
    UPDATE_TYPE_CHOICES = (
        ("work", "Occupation, studies, or industry"),
        ("location", "Current location"),
        ("story", "Profile story, memories, or advice"),
        ("photo", "Profile photograph"),
        ("identity", "Name or graduation year"),
        ("removal", "Profile removal"),
        ("other", "Something else"),
    )

    update_type = forms.ChoiceField(
        choices=UPDATE_TYPE_CHOICES,
        label="What needs updating?",
    )
    message = forms.CharField(
        label="Requested correction or update",
        widget=forms.Textarea(
            attrs={
                "rows": 7,
                "placeholder": (
                    "Tell us what is currently incorrect and what it should say…"
                ),
            }
        ),
    )


class AlumniStorySubmissionForm(PublicFormProtectionFieldsMixin, forms.ModelForm):
    class Meta:
        model = AlumniStory
        fields = (
            "full_name",
            "graduation_year",
            "email",
            "phone",
            "current_location",
            "occupation",
            "industry",
            "profile_photo",
            "life_story",
            "school_memories",
            "message_to_students",
            "consent_to_publish",
        )
        widgets = {
            "graduation_year": forms.NumberInput(
                attrs={"min": 1900, "max": date.today().year}
            ),
            "life_story": forms.Textarea(attrs={"rows": 7}),
            "school_memories": forms.Textarea(attrs={"rows": 5}),
            "message_to_students": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["life_story"].required = True
        self.fields["consent_to_publish"].help_text = (
            "I consent to my directory profile and photo being published on this website."
        )

    def clean_graduation_year(self):
        year = self.cleaned_data["graduation_year"]
        if year > date.today().year:
            raise forms.ValidationError("Graduation year cannot be in the future.")
        return year

    def clean_consent_to_publish(self):
        consent = self.cleaned_data["consent_to_publish"]
        if not consent:
            raise forms.ValidationError(
                "Consent is required before an alumni profile can be submitted."
            )
        return consent

class AlumniReviewForm(forms.ModelForm):
    class Meta:
        model = AlumniStory
        fields = ("status", "staff_notes")
        widgets = {
            "status": forms.Select(attrs={"class": "w-full rounded-xl border-stone-300"}),
            "staff_notes": forms.Textarea(
                attrs={
                    "rows": 5,
                    "class": "w-full rounded-xl border-stone-300",
                    "placeholder": "Private review notes or follow-up actions…",
                }
            ),
        }


class AlumniOpportunitySubmissionForm(PublicFormProtectionFieldsMixin, forms.ModelForm):
    verification_email = forms.EmailField(
        label="Email used for your alumni profile",
        help_text="This is checked privately and is not published.",
    )

    class Meta:
        model = AlumniOpportunity
        fields = (
            "alumni",
            "verification_email",
            "opportunity_type",
            "title",
            "provider",
            "summary",
            "application_url",
            "deadline",
        )
        labels = {"alumni": "Your verified alumni profile"}
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 6}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["alumni"].queryset = AlumniStory.objects.filter(
            status="approved", consent_to_publish=True
        ).order_by("full_name")

    def clean(self):
        cleaned_data = super().clean()
        alumni = cleaned_data.get("alumni")
        email = cleaned_data.get("verification_email")
        if alumni and email and alumni.email.casefold() != email.casefold():
            self.add_error(
                "verification_email",
                "That email does not match the selected verified profile.",
            )
        return cleaned_data


class AlumniOpportunityReviewForm(forms.ModelForm):
    class Meta:
        model = AlumniOpportunity
        fields = ("status", "staff_notes")
        widgets = {
            "status": forms.Select(attrs={"class": "w-full rounded-xl border-stone-300"}),
            "staff_notes": forms.Textarea(attrs={"rows": 5, "class": "w-full rounded-xl border-stone-300"}),
        }


class MentorshipRequestReviewForm(forms.ModelForm):
    class Meta:
        model = MentorshipRequest
        fields = ("is_handled", "staff_notes")
        labels = {"is_handled": "Request has been handled"}
        widgets = {
            "staff_notes": forms.Textarea(attrs={"rows": 5, "class": "w-full rounded-xl border-stone-300"}),
        }
