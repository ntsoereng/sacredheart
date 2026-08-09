import csv
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from apps.admissions.models import Application
from apps.alumni.forms import AlumniReviewForm
from apps.alumni.models import AlumniStory
from apps.core.models import ContactMessage, ExtracurricularActivity, SiteSettings
from apps.events.models import Event
from apps.posts.models import Post
from apps.academics.models import Subject
from apps.staff.models import StaffMember
from apps.portal.forms import (
    ApplicationNoteForm,
    ApplicationStatusForm,
    AnnouncementForm,
    StaffActivityForm,
    StaffEventForm,
    StaffMemberForm,
    StaffPostForm,
    SiteSettingsForm,
    StaffSubjectForm,
)
from apps.portal.mixins import (
    AnyStaffPermissionRequiredMixin,
    StaffPermissionRequiredMixin,
    StaffRequiredMixin,
)

class DashboardView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    template_name = "portal/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        applications = Application.objects.all()
        context.update({
            "new_applications": applications.filter(status="new").count(),
            "review_applications": applications.filter(status="review").count(),
            "accepted_applications": applications.filter(status="accepted").count(),
            "declined_applications": applications.filter(status="declined").count(),
            "recent_applications": applications.select_related("reviewed_by")[:6],
            "recent_messages": ContactMessage.objects.all()[:5],
            "pending_alumni": AlumniStory.objects.filter(status="pending").count(),
            "recent_alumni": AlumniStory.objects.select_related("reviewed_by")[:5],
        })
        return context


class ContentManagerView(LoginRequiredMixin, AnyStaffPermissionRequiredMixin, TemplateView):
    template_name = "portal/content_manager.html"
    permission_required = (
        "posts.view_post",
        "events.view_event",
        "academics.view_subject",
        "staff.view_staffmember",
        "core.view_extracurricularactivity",
        "core.change_sitesettings",
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts"] = Post.objects.select_related("author")[:10]
        context["events"] = Event.objects.select_related("created_by").order_by(
            "-event_date"
        )[:10]
        context["published_posts"] = Post.objects.filter(is_published=True).count()
        context["published_events"] = Event.objects.filter(is_published=True).count()
        context["subjects"] = Subject.objects.all()[:10]
        context["staff_members"] = StaffMember.objects.prefetch_related("subjects")[:10]
        context["active_subjects"] = Subject.objects.filter(is_active=True).count()
        context["active_staff"] = StaffMember.objects.filter(is_active=True).count()
        context["activities"] = ExtracurricularActivity.objects.all()[:10]
        context["published_activities"] = ExtracurricularActivity.objects.filter(
            is_published=True
        ).count()
        return context


class StaffContentFormMixin(LoginRequiredMixin, StaffPermissionRequiredMixin):
    template_name = "portal/content_form.html"

    def get_success_url(self):
        return reverse("content-manager")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["content_type"] = self.content_kind
        context["page_title"] = self.page_title
        context["is_editing"] = self.object is not None
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"{self.content_kind.title()} saved successfully.",
        )
        return response


class PostCreateView(StaffContentFormMixin, CreateView):
    permission_required = "posts.add_post"
    model = Post
    form_class = StaffPostForm
    content_kind = "news post"
    page_title = "Create news post"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(StaffContentFormMixin, UpdateView):
    permission_required = "posts.change_post"
    model = Post
    form_class = StaffPostForm
    content_kind = "news post"
    page_title = "Edit news post"


class EventCreateView(StaffContentFormMixin, CreateView):
    permission_required = "events.add_event"
    model = Event
    form_class = StaffEventForm
    content_kind = "event"
    page_title = "Create event"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class EventUpdateView(StaffContentFormMixin, UpdateView):
    permission_required = "events.change_event"
    model = Event
    form_class = StaffEventForm
    content_kind = "event"
    page_title = "Edit event"


class SubjectCreateView(StaffContentFormMixin, CreateView):
    permission_required = "academics.add_subject"
    model = Subject
    form_class = StaffSubjectForm
    content_kind = "subject"
    page_title = "Create subject"


class SubjectUpdateView(StaffContentFormMixin, UpdateView):
    permission_required = "academics.change_subject"
    model = Subject
    form_class = StaffSubjectForm
    content_kind = "subject"
    page_title = "Edit subject"


class StaffMemberCreateView(StaffContentFormMixin, CreateView):
    permission_required = "staff.add_staffmember"
    model = StaffMember
    form_class = StaffMemberForm
    content_kind = "staff member"
    page_title = "Create staff profile"


class StaffMemberUpdateView(StaffContentFormMixin, UpdateView):
    permission_required = "staff.change_staffmember"
    model = StaffMember
    form_class = StaffMemberForm
    content_kind = "staff member"
    page_title = "Edit staff profile"


class ActivityCreateView(StaffContentFormMixin, CreateView):
    permission_required = "core.add_extracurricularactivity"
    model = ExtracurricularActivity
    form_class = StaffActivityForm
    content_kind = "activity"
    page_title = "Create club or activity"


class ActivityUpdateView(StaffContentFormMixin, UpdateView):
    permission_required = "core.change_extracurricularactivity"
    model = ExtracurricularActivity
    form_class = StaffActivityForm
    content_kind = "activity"
    page_title = "Edit club or activity"


class AnnouncementUpdateView(LoginRequiredMixin, StaffPermissionRequiredMixin, UpdateView):
    permission_required = "core.change_sitesettings"
    model = SiteSettings
    form_class = AnnouncementForm
    template_name = "portal/announcement_form.html"

    def get_object(self, queryset=None):
        return SiteSettings.objects.first()

    def get_success_url(self):
        return reverse("content-manager")

    def form_valid(self, form):
        messages.success(self.request, "Homepage announcement updated.")
        return super().form_valid(form)


class SiteSettingsUpdateView(LoginRequiredMixin, StaffPermissionRequiredMixin, UpdateView):
    permission_required = "core.change_sitesettings"
    model = SiteSettings
    form_class = SiteSettingsForm
    template_name = "portal/site_settings.html"

    def get_object(self, queryset=None):
        settings = SiteSettings.objects.first()
        if settings is None:
            settings = SiteSettings.objects.create(
                school_name="Sacred Heart High School"
            )
        return settings

    def get_success_url(self):
        return reverse("site-settings")

    def form_valid(self, form):
        messages.success(self.request, "Site settings updated successfully.")
        return super().form_valid(form)
    
    
class ApplicationListView(LoginRequiredMixin, StaffPermissionRequiredMixin, ListView):
    permission_required = "admissions.view_application"
    model = Application
    template_name = "portal/applications.html"
    context_object_name = "applications"
    paginate_by = 25
    
    def get_queryset(self):

        queryset = Application.objects.all()

        search = self.request.GET.get(
            "q",
            ""
        ).strip()

        year = self.request.GET.get(
            "year",
            ""
        ).strip()

        status = self.request.GET.get(
            "status",
            ""
        ).strip()

        if search:

            queryset = queryset.filter(

                Q(student_name__icontains=search)

                |

                Q(student_surname__icontains=search)

                |

                Q(parent_guardian_names__icontains=search)

                |

                Q(parent_phone_number__icontains=search)

                |

                Q(parent_guardian_email__icontains=search)

                |

                Q(reference_number__icontains=search)
            )

        if year:

            queryset = queryset.filter(
                academic_year=year
            )

        if status:

            queryset = queryset.filter(
                status=status
            )

        return queryset
    
    
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["available_years"] = (
            Application.objects
            .values_list(
                "academic_year",
                flat=True
            )
            .distinct()
            .order_by("-academic_year")
        )

        context["status_choices"] = (
            Application.STATUS_CHOICES
        )

        context["new_count"] = Application.objects.filter(status="new").count()
        context["review_count"] = Application.objects.filter(status="review").count()
        context["accepted_count"] = Application.objects.filter(status="accepted").count()
        context["declined_count"] = Application.objects.filter(status="declined").count()

        return context
    

class ApplicationDetailView(LoginRequiredMixin, StaffPermissionRequiredMixin, DetailView):
    permission_required = "admissions.view_application"
    model = Application

    template_name = (
        "portal/application_detail.html"
    )

    context_object_name = "application"

    def get_queryset(self):
        return super().get_queryset().select_related("reviewed_by").prefetch_related(
            "review_notes__author"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault(
            "status_form",
            ApplicationStatusForm(instance=self.object),
        )
        context.setdefault("note_form", ApplicationNoteForm())
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm("admissions.change_application"):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        self.object = self.get_object()
        action = request.POST.get("action")

        if action == "update_status":
            form = ApplicationStatusForm(request.POST, instance=self.object)
            if form.is_valid():
                application = form.save(commit=False)
                application.reviewed = application.status != "new"
                application.reviewed_by = request.user
                application.reviewed_at = timezone.now()
                application.save(
                    update_fields=["status", "reviewed", "reviewed_by", "reviewed_at"]
                )
                messages.success(
                    request,
                    f"Application status updated to {application.get_status_display()}.",
                )
                return redirect("application-detail", pk=application.pk)

            return self.render_to_response(
                self.get_context_data(status_form=form)
            )

        if action == "add_note":
            form = ApplicationNoteForm(request.POST)
            if form.is_valid():
                note = form.save(commit=False)
                note.application = self.object
                note.author = request.user
                note.save()
                messages.success(request, "Internal note added.")
                return redirect("application-detail", pk=self.object.pk)

            return self.render_to_response(
                self.get_context_data(note_form=form)
            )

        messages.error(request, "Please choose a valid application action.")
        return redirect("application-detail", pk=self.object.pk)


class AlumniReviewListView(LoginRequiredMixin, StaffPermissionRequiredMixin, ListView):
    permission_required = "alumni.view_alumnistory"
    model = AlumniStory
    template_name = "portal/alumni_list.html"
    context_object_name = "stories"
    paginate_by = 25

    def get_queryset(self):
        queryset = AlumniStory.objects.select_related("reviewed_by")
        status = self.request.GET.get("status", "").strip()
        query = self.request.GET.get("q", "").strip()
        if status:
            queryset = queryset.filter(status=status)
        if query:
            queryset = queryset.filter(
                Q(full_name__icontains=query)
                | Q(email__icontains=query)
                | Q(occupation__icontains=query)
                | Q(graduation_year__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = AlumniStory.STATUS_CHOICES
        context["pending_count"] = AlumniStory.objects.filter(status="pending").count()
        context["approved_count"] = AlumniStory.objects.filter(status="approved").count()
        context["rejected_count"] = AlumniStory.objects.filter(status="rejected").count()
        return context


class AlumniReviewDetailView(LoginRequiredMixin, StaffPermissionRequiredMixin, DetailView):
    permission_required = "alumni.view_alumnistory"
    model = AlumniStory
    template_name = "portal/alumni_detail.html"
    context_object_name = "story"

    def get_queryset(self):
        return super().get_queryset().select_related("reviewed_by")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("review_form", AlumniReviewForm(instance=self.object))
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm("alumni.change_alumnistory"):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        self.object = self.get_object()
        form = AlumniReviewForm(request.POST, instance=self.object)
        if form.is_valid():
            story = form.save(commit=False)
            story.mark_reviewed(request.user)
            story.save()
            messages.success(
                request,
                f"Alumni submission updated to {story.get_status_display()}.",
            )
            return redirect("alumni-review-detail", pk=story.pk)
        return self.render_to_response(self.get_context_data(review_form=form))

    
class ApplicationExportView(LoginRequiredMixin, StaffPermissionRequiredMixin, View):
    permission_required = "admissions.view_application"

    def get(self, request):

        response = HttpResponse(
            content_type="text/csv"
        )

        response[
            "Content-Disposition"
        ] = (
            'attachment; filename="applications.csv"'
        )

        writer = csv.writer(response)

        writer.writerow([
            "Reference",
            "Status",
            "Academic Year",
            "Student Name",
            "Student Surname",
            "Date Of Birth",
            "Nationality",
            "Guardian",
            "Phone",
            "Email",
            "Address",
            "Previous School",
            "Student Candidate Number",
            "District",
            "Submitted",
        ])

        for app in Application.objects.all():

            writer.writerow([
                app.reference_number,
                app.get_status_display(),
                app.academic_year,
                app.student_name,
                app.student_surname,
                app.date_of_birth,
                app.nationality,
                app.parent_guardian_names,
                app.parent_phone_number,
                app.parent_guardian_email,
                app.home_address,
                app.previous_school,
                app.student_candidate_number,
                app.district,
                app.submitted_at,
            ])

        return response
    
    
class MessageListView(LoginRequiredMixin, StaffPermissionRequiredMixin, ListView):
    permission_required = "core.view_contactmessage"

    model = ContactMessage

    template_name = "portal/messages.html"

    context_object_name = "contact_messages"

    paginate_by = 25    
    
    
    
class MessageDetailView(LoginRequiredMixin, StaffPermissionRequiredMixin, DetailView):
    permission_required = "core.view_contactmessage"

    model = ContactMessage

    template_name = "portal/message_detail.html"

    context_object_name = "contact_message"

    def get_object(self):

        contact_message = super().get_object()

        if not contact_message.is_read:

            contact_message.is_read = True

            contact_message.save(
                update_fields=["is_read"]
            )

        return contact_message
