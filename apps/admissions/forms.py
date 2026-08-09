from datetime import date

from django import forms

from apps.admissions.models import Application


class ApplicationForm(forms.ModelForm):

    parent_guardian_email = forms.EmailField(
        label="Parent/guardian email",
        help_text="We will send the application reference to this address.",
        widget=forms.EmailInput(
            attrs={
                "class": "w-full",
                "autocomplete": "email",
                "inputmode": "email",
                "placeholder": "parent.guardian@example.com",
            }
        ),
    )

    class Meta:
        model = Application
        fields = (
            "academic_year",
            "student_name",
            "student_surname",
            "date_of_birth",
            "nationality",
            "parent_guardian_names",
            "parent_phone_number",
            "parent_guardian_email",
            "home_address",
            "previous_school",
            "student_candidate_number",
            "district",
        )

        widgets = {
            "academic_year": forms.TextInput(
                attrs={
                    "readonly": True,
                    "class": "w-full"
                }
            ),
            "student_name": forms.TextInput(
                attrs={
                    "class": "w-full",
                    "autocomplete": "given-name",
                    "placeholder": "Student’s first name",
                }
            ),
            "student_surname": forms.TextInput(
                attrs={
                    "class": "w-full",
                    "autocomplete": "family-name",
                    "placeholder": "Student’s surname",
                }
            ),
            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full",
                    "max": date.today().isoformat(),
                }
            ),
            "nationality": forms.TextInput(
                attrs={
                    "class": "w-full",
                    "autocomplete": "country-name",
                    "placeholder": "e.g. Lesotho",
                }
            ),
            "parent_guardian_names": forms.TextInput(
                attrs={
                    "class": "w-full",
                    "autocomplete": "name",
                    "placeholder": "Parent/guardian’s full name",
                }
            ),
            "parent_phone_number": forms.TextInput(
                attrs={
                    "class": "w-full",
                    "autocomplete": "tel",
                    "inputmode": "tel",
                    "placeholder": "+266 …",
                }
            ),
            "home_address": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "w-full",
                    "autocomplete": "street-address",
                    "placeholder": "Village, town and other address details",
                }
            ),
            "previous_school": forms.TextInput(
                attrs={
                    "class": "w-full",
                    "placeholder": "Name of previous school",
                }
            ),
            "student_candidate_number": forms.TextInput(
                attrs={
                    "class": "w-full",
                    "placeholder": "Candidate number from previous school",
                }
            ),
            "district": forms.Select(
                attrs={"class": "w-full"}
            ),
        }
