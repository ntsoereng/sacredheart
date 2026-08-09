from datetime import date
import logging

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from apps.core.models import SiteSettings
from apps.core.throttling import RateLimitMixin

from .forms import ApplicationForm
from .emails import send_application_confirmation


logger = logging.getLogger(__name__)


class ApplicationCreateView(RateLimitMixin, FormView):
    rate_limit_count = 5
    rate_limit_window = 3600
    rate_limit_scope = "admissions-application"

    template_name = "admissions/application_form.html"

    form_class = ApplicationForm

    success_url = reverse_lazy(
        "application-success"
    )

    def dispatch(self, request, *args, **kwargs):
        self.admissions_open = SiteSettings.objects.filter(
            admissions_open=True
        ).exists()

        if not self.admissions_open:
            return self.render_to_response({"admissions_open": False})

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["admissions_open"] = self.admissions_open

        return context

    def get_initial(self):

        initial = super().get_initial()

        initial["academic_year"] = (
            str(date.today().year + 1)
        )

        return initial

    def form_valid(self, form):

        application = form.save()

        self.request.session[
            "latest_application_reference"
        ] = application.reference_number

        try:
            confirmation_sent = send_application_confirmation(application)
        except Exception:
            confirmation_sent = False
            logger.exception(
                "Could not send confirmation for application %s",
                application.reference_number,
            )
        self.request.session["application_confirmation_email_sent"] = confirmation_sent

        messages.success(
            self.request,
            "Application submitted successfully."
        )

        return super().form_valid(form)
    
    
class ApplicationSuccessView(TemplateView):

    template_name = "admissions/application_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reference_number"] = self.request.session.get(
            "latest_application_reference"
        )
        context["confirmation_email_sent"] = self.request.session.get(
            "application_confirmation_email_sent",
            False,
        )
        return context
