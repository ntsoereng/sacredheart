import csv
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views import View
from django.views.generic import (
    DetailView,
    ListView,
    TemplateView,
)

from apps.admissions.models import Application
from apps.core.models import ContactMessage
from apps.portal.mixins import StaffRequiredMixin

class DashboardView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    template_name = "portal/dashboard.html"
    
    
class ApplicationListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
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

        return context
    

class ApplicationDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = Application

    template_name = (
        "portal/application_detail.html"
    )

    context_object_name = "application"

    
class ApplicationExportView(LoginRequiredMixin, StaffRequiredMixin, View):

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
            "Academic Year",
            "Student Name",
            "Student Surname",
            "Date Of Birth",
            "Guardian",
            "Phone",
            "Address",
            "Previous School",
            "District",
            "Submitted",
        ])

        for app in Application.objects.all():

            writer.writerow([
                app.academic_year,
                app.student_name,
                app.student_surname,
                app.date_of_birth,
                app.parent_guardian_names,
                app.parent_phone_number,
                app.home_address,
                app.previous_school,
                app.district,
                app.submitted_at,
            ])

        return response
    
    
class MessageListView(LoginRequiredMixin, StaffRequiredMixin, ListView):

    model = ContactMessage

    template_name = "portal/messages.html"

    context_object_name = "contact_messages"

    paginate_by = 25    
    
    
    
class MessageDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):

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