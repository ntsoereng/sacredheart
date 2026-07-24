from django import forms
from django.utils.html import strip_tags

from apps.admissions.models import Application, ApplicationNote
from apps.events.models import Event
from apps.posts.models import Post
from apps.posts.content import sanitize_post_html
from apps.academics.models import Subject
from apps.staff.models import StaffMember


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
            "description": forms.Textarea(
                attrs={"rows": 7, "placeholder": "What should families know?"}
            ),
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "location": forms.TextInput(attrs={"placeholder": "Venue or location"}),
        }


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
            "description": forms.Textarea(
                attrs={"rows": 8, "placeholder": "Describe what learners study…"}
            ),
        }


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
            "short_bio": forms.Textarea(
                attrs={"rows": 6, "placeholder": "A short public biography…"}
            ),
            "motto": forms.TextInput(attrs={"placeholder": "Optional motto"}),
            "started_at_shhs": forms.DateInput(attrs={"type": "date"}),
            "subjects": forms.CheckboxSelectMultiple(),
            "welcome_remarks": forms.Textarea(attrs={"rows": 6}),
        }


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
