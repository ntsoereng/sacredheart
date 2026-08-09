from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import StaffAuthenticationForm, StaffRegistrationForm


class StaffLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = StaffAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy("dashboard")


class StaffLogoutView(LogoutView):
    next_page = reverse_lazy("home")


class StaffRegistrationView(FormView):
    template_name = "accounts/register.html"
    form_class = StaffRegistrationForm
    success_url = reverse_lazy("staff-registration-complete")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
