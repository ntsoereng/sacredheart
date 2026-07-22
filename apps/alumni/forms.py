from datetime import date

from django import forms

from .models import AlumniStory


class AlumniStorySubmissionForm(forms.ModelForm):
    class Meta:
        model = AlumniStory
        fields = (
            "full_name",
            "graduation_year",
            "email",
            "phone",
            "current_location",
            "occupation",
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

    def clean_graduation_year(self):
        year = self.cleaned_data["graduation_year"]
        if year > date.today().year:
            raise forms.ValidationError("Graduation year cannot be in the future.")
        return year

    def clean_consent_to_publish(self):
        consent = self.cleaned_data["consent_to_publish"]
        if not consent:
            raise forms.ValidationError(
                "Consent is required before an alumni story can be submitted."
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
