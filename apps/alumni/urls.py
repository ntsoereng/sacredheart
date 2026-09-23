from django.http import Http404
from django.urls import path, re_path

from .views import (
    AlumniProfileUpdateRequestView,
    AlumniProfileUpdateSentView,
    AlumniStoryCreateView,
    AlumniStoryDetailView,
    AlumniStoryListView,
    AlumniStorySuccessView,
    AlumniVerifiedProfileUpdateView,
)

def opportunities_unavailable(request):
    """Keep the public module offline while it is being revised."""
    raise Http404


urlpatterns = [
    re_path(r"^alumni/opportunities(?:/.*)?$", opportunities_unavailable),
    path("alumni/", AlumniStoryListView.as_view(), name="alumni-list"),
    path(
        "alumni/classes/<int:year>/",
        AlumniStoryListView.as_view(),
        name="alumni-class",
    ),
    path("alumni/share/", AlumniStoryCreateView.as_view(), name="alumni-create"),
    path("alumni/thank-you/", AlumniStorySuccessView.as_view(), name="alumni-success"),
    path("alumni/<slug:slug>/request-update/", AlumniProfileUpdateRequestView.as_view(), name="alumni-profile-update"),
    path("alumni/<slug:slug>/request-update/check-email/", AlumniProfileUpdateSentView.as_view(), name="alumni-profile-update-sent"),
    path("alumni/<slug:slug>/request-update/<str:token>/", AlumniVerifiedProfileUpdateView.as_view(), name="alumni-profile-update-confirm"),
    path("alumni/<slug:slug>/", AlumniStoryDetailView.as_view(), name="alumni-detail"),
]
