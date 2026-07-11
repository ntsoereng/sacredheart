from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from .forms import StaffAuthenticationForm


class StaffLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = StaffAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy("dashboard")


class StaffLogoutView(LogoutView):
    next_page = reverse_lazy("home")
