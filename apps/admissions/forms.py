from django import forms

from apps.admissions.models import Application


class ApplicationForm(forms.ModelForm):

    class Meta:
        model = Application
        fields = (
            "academic_year",
            "student_name",
            "student_surname",
            "date_of_birth",
            "parent_guardian_names",
            "parent_phone_number",
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
                attrs={"class": "w-full"}
            ),
            "student_surname": forms.TextInput(
                attrs={"class": "w-full"}
            ),
            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full"
                }
            ),
            "parent_guardian_names": forms.TextInput(
                attrs={"class": "w-full"}
            ),
            "parent_phone_number": forms.TextInput(
                attrs={"class": "w-full"}
            ),
            "home_address": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "w-full"
                }
            ),
            "previous_school": forms.TextInput(
                attrs={"class": "w-full"}
            ),
            "district": forms.Select(
                attrs={"class": "w-full"}
            ),
        }