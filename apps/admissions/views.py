from datetime import date
import logging

from django.contrib import messages
from django.db import IntegrityError, OperationalError, transaction
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from apps.core.models import SiteSettings

from .forms import ApplicationForm, DUPLICATE_APPLICATION_MESSAGE
from .emails import send_application_confirmation
from .protection import (
    admission_attempt_is_limited,
    consume_submission_token,
    create_submission_token,
    submission_token_is_available,
)


logger = logging.getLogger(__name__)


class ApplicationCreateView(FormView):
    template_name = "admissions/application_form.html"

    form_class = ApplicationForm

    success_url = reverse_lazy(
        "application-success"
    )

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST" and admission_attempt_is_limited(request):
            response = render(
                request,
                "admissions/application_error.html",
                {
                    "error_title": "Please wait before trying again",
                    "error_message": (
                        "We have received too many application attempts. Please "
                        "wait before trying again, or contact the school if you need help."
                    ),
                },
                status=429,
            )
            response["Retry-After"] = "3600"
            return response

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

    def post(self, request, *args, **kwargs):
        if request.POST.get("website", "").strip():
            return render(
                request,
                "admissions/application_error.html",
                {
                    "error_title": "We could not submit the application",
                    "error_message": (
                        "Please return to the application form and try again. If "
                        "the problem continues, contact the school for assistance."
                    ),
                },
                status=400,
            )
        if not submission_token_is_available(request.POST.get("submission_token")):
            return self._invalid_token_response()
        return super().post(request, *args, **kwargs)

    def get_initial(self):

        initial = super().get_initial()

        initial["academic_year"] = (
            str(date.today().year + 1)
        )
        if self.request.method == "GET":
            initial["submission_token"] = create_submission_token()

        return initial

    def form_invalid(self, form):
        if "submission_token" in form.errors:
            return self._invalid_token_response()
        return super().form_invalid(form)

    def _invalid_token_response(self):
        return render(
            self.request,
            "admissions/application_error.html",
            {
                "error_title": "This application form is no longer valid",
                "error_message": (
                    "The form may have expired or already been submitted. Open a "
                    "fresh application form before trying again."
                ),
            },
            status=409,
        )

    def _possible_duplicate_response(self):
        return render(
            self.request,
            "admissions/application_error.html",
            {
                "error_title": "Your application may already be recorded",
                "error_message": DUPLICATE_APPLICATION_MESSAGE,
            },
            status=409,
        )

    def form_valid(self, form):
        if not consume_submission_token(form.cleaned_data["submission_token"]):
            return self._invalid_token_response()

        try:
            with transaction.atomic():
                application = form.save()
        except IntegrityError:
            logger.info("A duplicate application insert was prevented.")
            return self._possible_duplicate_response()
        except OperationalError:
            logger.warning(
                "An application insert could not complete because the database was busy."
            )
            return self._possible_duplicate_response()

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
