from django.urls import path

from .views import StaffLoginView, StaffLogoutView


urlpatterns = [
    path("staff/login/", StaffLoginView.as_view(), name="staff-login"),
    path("staff/logout/", StaffLogoutView.as_view(), name="staff-logout"),
]
