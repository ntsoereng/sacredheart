from django.urls import path

from .views import ApplicationCreateView, ApplicationSuccessView

urlpatterns = [
    path("admissions/", ApplicationCreateView.as_view(), name="application-create"),
    path("admissions/success/", ApplicationSuccessView.as_view(), name="application-success"),
]