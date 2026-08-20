from datetime import date

from django import forms

from apps.admissions.models import Application, normalize_identity_value


DUPLICATE_APPLICATION_MESSAGE = (
    "An application for this learner and academic year may already have been "
    "received. Please check your records or contact the school before trying again."
)


class ApplicationForm(forms.ModelForm):

    website = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "tabindex": "-1",
                "autocomplete": "off",
                "aria-hidden": "true",
            }
        ),
    )

    submission_token = forms.CharField(widget=forms.HiddenInput())

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

    previous_school = forms.CharField(
        label="Previous school",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "w-full",
                "placeholder": "Name of previous school",
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
            "district": forms.Select(
                attrs={"class": "w-full"}
            ),
        }

    def clean_academic_year(self):
        return " ".join(self.cleaned_data["academic_year"].split())

    def clean_student_name(self):
        return " ".join(self.cleaned_data["student_name"].split())

    def clean_student_surname(self):
        return " ".join(self.cleaned_data["student_surname"].split())

    def clean_parent_guardian_email(self):
        return self.cleaned_data["parent_guardian_email"].strip().casefold()

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("website"):
            raise forms.ValidationError(
                "We could not process this application. Please return and try again."
            )

        identity_fields = (
            cleaned_data.get("academic_year"),
            cleaned_data.get("student_name"),
            cleaned_data.get("student_surname"),
            cleaned_data.get("date_of_birth"),
        )
        if all(identity_fields):
            duplicate_exists = Application.objects.filter(
                normalized_academic_year=normalize_identity_value(identity_fields[0]),
                normalized_student_name=normalize_identity_value(identity_fields[1]),
                normalized_student_surname=normalize_identity_value(identity_fields[2]),
                date_of_birth=identity_fields[3],
            ).exists()
            if duplicate_exists:
                raise forms.ValidationError(DUPLICATE_APPLICATION_MESSAGE)
        return cleaned_data
