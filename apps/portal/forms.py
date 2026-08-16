import html
import re
from urllib.parse import urlparse

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.html import strip_tags

from apps.admissions.models import Application, ApplicationNote
from apps.events.models import Event
from apps.posts.models import Post
from apps.posts.content import sanitize_post_html
from apps.academics.models import Subject
from apps.core.models import ExtracurricularActivity, SiteSettings
from apps.staff.models import StaffMember
from apps.vacancies.models import Vacancy


def _clean_rich_text(value, required_message):
    cleaned = sanitize_post_html(value)
    if not strip_tags(cleaned).strip():
        raise forms.ValidationError(required_message)
    return cleaned


class StaffPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "title",
            "summary",
            "content",
            "featured_image",
            "is_published",
            "featured",
        )
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "News story title"}),
            "summary": forms.Textarea(
                attrs={"rows": 3, "placeholder": "A short summary for news cards"}
            ),
            "content": forms.HiddenInput(),
        }

    def clean_content(self):
        content = self.cleaned_data["content"]
        cleaned = sanitize_post_html(content)
        if not strip_tags(cleaned).strip():
            raise forms.ValidationError("Please add the news story content.")
        return cleaned


class StaffEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = (
            "title",
            "description",
            "event_date",
            "location",
            "image",
            "is_published",
            "featured",
        )
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Event title"}),
            "description": forms.HiddenInput(),
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "location": forms.TextInput(attrs={"placeholder": "Venue or location"}),
        }

    def clean_description(self):
        return _clean_rich_text(
            self.cleaned_data["description"],
            "Please add the event description.",
        )


class StaffVacancyForm(forms.ModelForm):
    rich_text_fields = (
        "job_description",
        "minimum_qualifications",
        "experience_requirements",
        "skills_competencies",
        "additional_requirements",
        "application_instructions",
    )

    class Meta:
        model = Vacancy
        fields = (
            "job_title", "department", "employment_type", "location",
            "application_deadline", "expected_start_date", "status",
            "reference_number", "short_summary", "job_description",
            "minimum_qualifications", "experience_requirements",
            "skills_competencies", "additional_requirements",
            "application_instructions", "contact_email", "contact_person",
            "is_published",
        )
        widgets = {
            "application_deadline": forms.DateInput(attrs={"type": "date"}),
            "expected_start_date": forms.DateInput(attrs={"type": "date"}),
            "short_summary": forms.Textarea(attrs={"rows": 3}),
            "job_description": forms.HiddenInput(),
            "minimum_qualifications": forms.HiddenInput(),
            "experience_requirements": forms.HiddenInput(),
            "skills_competencies": forms.HiddenInput(),
            "additional_requirements": forms.HiddenInput(),
            "application_instructions": forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        required = {
            "job_description": "Please add the job description.",
            "minimum_qualifications": "Please add the minimum qualifications.",
            "experience_requirements": "Please add the experience requirements.",
            "skills_competencies": "Please add the skills or competencies.",
            "application_instructions": "Please add application instructions.",
        }
        for field, message in required.items():
            value = cleaned_data.get(field)
            if value is not None:
                try:
                    cleaned_data[field] = _clean_rich_text(value, message)
                except forms.ValidationError as error:
                    self.add_error(field, error)
        additional = cleaned_data.get("additional_requirements")
        if additional:
            cleaned_data["additional_requirements"] = sanitize_post_html(additional)
        return cleaned_data


class StaffSubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = (
            "name",
            "description",
            "featured_image",
            "display_order",
            "is_active",
        )
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Subject name"}),
            "description": forms.HiddenInput(),
        }

    def clean_description(self):
        return _clean_rich_text(
            self.cleaned_data["description"],
            "Please add the subject description.",
        )


class StaffMemberForm(forms.ModelForm):
    class Meta:
        model = StaffMember
        fields = (
            "full_name",
            "role",
            "profile_picture",
            "short_bio",
            "motto",
            "started_at_shhs",
            "subjects",
            "is_principal",
            "welcome_remarks",
            "display_order",
            "is_active",
        )
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Full name"}),
            "role": forms.TextInput(attrs={"placeholder": "Teacher, Principal…"}),
            "short_bio": forms.HiddenInput(),
            "motto": forms.TextInput(attrs={"placeholder": "Optional motto"}),
            "started_at_shhs": forms.DateInput(attrs={"type": "date"}),
            "subjects": forms.CheckboxSelectMultiple(),
            "welcome_remarks": forms.HiddenInput(),
        }

    def clean_short_bio(self):
        return _clean_rich_text(
            self.cleaned_data["short_bio"],
            "Please add a short biography.",
        )

    def clean_welcome_remarks(self):
        value = self.cleaned_data.get("welcome_remarks", "")
        return sanitize_post_html(value) if value else ""


class StaffActivityForm(forms.ModelForm):
    class Meta:
        model = ExtracurricularActivity
        fields = (
            "name",
            "category",
            "short_description",
            "description",
            "achievements",
            "featured_image",
            "is_featured",
            "is_published",
            "display_order",
        )
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Club or activity name"}),
            "short_description": forms.Textarea(
                attrs={"rows": 3, "placeholder": "A concise public selling point"}
            ),
            "description": forms.HiddenInput(),
            "achievements": forms.HiddenInput(),
        }

    def clean_description(self):
        return _clean_rich_text(
            self.cleaned_data["description"],
            "Please add the activity description.",
        )

    def clean_achievements(self):
        value = self.cleaned_data.get("achievements", "")
        return sanitize_post_html(value) if value else ""


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = ("homepage_announcement", "show_announcement")
        widgets = {
            "homepage_announcement": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Write a short, timely school announcement.",
                }
            ),
        }


class SiteSettingsForm(forms.ModelForm):
    google_maps_embed_url = forms.CharField(
        required=False,
        label="Google Maps embed code or URL",
        help_text=(
            "In Google Maps choose Share, then Embed a map, and paste either the "
            "complete iframe code or its https://www.google.com/maps/embed URL."
        ),
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": '<iframe src="https://www.google.com/maps/embed?pb=…"></iframe>',
            }
        ),
    )

    class Meta:
        model = SiteSettings
        fields = (
            "school_name",
            "tagline",
            "logo",
            "favicon",
            "email",
            "phone",
            "address",
            "office_hours",
            "google_maps_embed_url",
            "facebook_url",
            "instagram_url",
            "youtube_url",
            "tiktok_url",
            "x_url",
            "hero_title",
            "hero_subtitle",
            "hero_image",
            "about_history",
            "about_mission",
            "about_vision",
            "about_values",
            "admissions_email",
            "admissions_open",
            "admissions_closing_date",
            "admissions_message",
            "admissions_list",
        )
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "hero_subtitle": forms.Textarea(attrs={"rows": 3}),
            "about_history": forms.Textarea(attrs={"rows": 5}),
            "about_mission": forms.Textarea(attrs={"rows": 4}),
            "about_vision": forms.Textarea(attrs={"rows": 4}),
            "about_values": forms.Textarea(attrs={"rows": 5}),
            "admissions_message": forms.Textarea(attrs={"rows": 3}),
            "admissions_closing_date": forms.DateInput(attrs={"type": "date"}),
            "facebook_url": forms.URLInput(attrs={"placeholder": "https://facebook.com/your-page"}),
            "instagram_url": forms.URLInput(attrs={"placeholder": "https://instagram.com/your-handle"}),
            "youtube_url": forms.URLInput(attrs={"placeholder": "https://youtube.com/@your-channel"}),
            "tiktok_url": forms.URLInput(attrs={"placeholder": "https://tiktok.com/@your-handle"}),
            "x_url": forms.URLInput(attrs={"placeholder": "https://x.com/your-handle"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        control_classes = "w-full max-w-full rounded-xl border-stone-300"
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = control_classes

    def clean_google_maps_embed_url(self):
        value = self.cleaned_data.get("google_maps_embed_url", "").strip()
        if not value:
            return ""

        iframe_src = re.search(
            r"<iframe[^>]+src\s*=\s*(['\"])(.*?)\1",
            value,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if iframe_src:
            value = html.unescape(iframe_src.group(2).strip())

        try:
            URLValidator(schemes=("https",))(value)
        except ValidationError:
            raise ValidationError(
                "Paste the Google Maps iframe code or its HTTPS embed URL."
            )

        parsed = urlparse(value)
        if parsed.hostname not in {"google.com", "www.google.com"} or not parsed.path.startswith(
            "/maps/embed"
        ):
            raise ValidationError(
                "This is not an embeddable Google Maps URL. In Google Maps, use "
                "Share > Embed a map instead of Copy link."
            )
        return value


class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ("status",)
        widgets = {
            "status": forms.Select(
                attrs={
                    "class": "w-full rounded-xl border-stone-300",
                }
            ),
        }


class ApplicationNoteForm(forms.ModelForm):
    class Meta:
        model = ApplicationNote
        fields = ("body",)
        labels = {"body": "Add an internal note"}
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Record findings, follow-up actions, or decision context…",
                    "class": "w-full rounded-xl border-stone-300",
                }
            ),
        }
