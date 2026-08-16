from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.db import transaction

from apps.academics.models import Subject
from apps.core.forms import PublicFormProtectionFieldsMixin
from apps.staff.models import StaffMember


class StaffAuthenticationForm(PublicFormProtectionFieldsMixin, AuthenticationForm):
    """Authenticate only accounts that are permitted to use the staff portal."""

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise ValidationError(
                "This account does not have access to the staff portal.",
                code="staff_access_required",
            )


class StaffRegistrationForm(PublicFormProtectionFieldsMixin, UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    full_name = forms.CharField(max_length=200)
    role = forms.CharField(max_length=150, initial="Teacher")
    profile_picture = forms.ImageField(required=False)
    short_bio = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}))
    motto = forms.CharField(max_length=255, required=False)
    started_at_shhs = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subjects"].queryset = (
            Subject.objects.filter(is_active=True)
            .order_by("name")
        )
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} w-full".strip()

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_staff = False
        if commit:
            user.save()
            profile = StaffMember.objects.create(
                user=user,
                full_name=self.cleaned_data["full_name"],
                role=self.cleaned_data["role"],
                profile_picture=self.cleaned_data.get("profile_picture"),
                short_bio=self.cleaned_data["short_bio"],
                motto=self.cleaned_data.get("motto", ""),
                started_at_shhs=self.cleaned_data.get("started_at_shhs"),
                is_active=False,
            )
            profile.subjects.set(self.cleaned_data["subjects"])
        return user
