from datetime import date

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from apps.core.models import SiteSettings

from .forms import ApplicationForm


class ApplicationCreateView(FormView):

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
        return context
