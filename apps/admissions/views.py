from datetime import date

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import ApplicationForm


class ApplicationCreateView(FormView):

    template_name = "admissions/application_form.html"

    form_class = ApplicationForm

    success_url = reverse_lazy(
        "application-success"
    )

    def get_initial(self):

        initial = super().get_initial()

        initial["academic_year"] = (
            str(date.today().year + 1)
        )

        return initial

    def form_valid(self, form):

        form.save()

        messages.success(
            self.request,
            "Application submitted successfully. We will review your application and get back to you soon."
        )

        return super().form_valid(form)
    
    
class ApplicationSuccessView(TemplateView):

    template_name = "admissions/application_success.html"