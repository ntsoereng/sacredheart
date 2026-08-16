from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import FormView

from apps.core.throttling import PublicFormProtectionMixin

from .forms import StaffAuthenticationForm, StaffRegistrationForm


class StaffLoginView(PublicFormProtectionMixin, LoginView):
    rate_limit_count = 10
    rate_limit_window = 300
    rate_limit_scope = "staff-login"
    template_name = "accounts/login.html"
    authentication_form = StaffAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy("dashboard")


class StaffLogoutView(LogoutView):
    next_page = reverse_lazy("home")


class StaffRegistrationView(PublicFormProtectionMixin, FormView):
    rate_limit_count = 5
    rate_limit_window = 3600
    rate_limit_scope = "staff-access-request"
    template_name = "accounts/register.html"
    form_class = StaffRegistrationForm
    success_url = reverse_lazy("staff-registration-complete")

    def protected_form_valid(self, form):
        form.save()
        return super().protected_form_valid(form)
