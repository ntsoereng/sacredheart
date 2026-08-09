from django.urls import path
from django.views.generic import TemplateView

from .views import StaffLoginView, StaffLogoutView, StaffRegistrationView


urlpatterns = [
    path("staff/login/", StaffLoginView.as_view(), name="staff-login"),
    path("staff/logout/", StaffLogoutView.as_view(), name="staff-logout"),
    path("staff/access-request/", StaffRegistrationView.as_view(), name="staff-register"),
    path(
        "staff/access-request/received/",
        TemplateView.as_view(template_name="accounts/register_complete.html"),
        name="staff-registration-complete",
    ),
]
