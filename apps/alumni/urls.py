from django.urls import path

from .views import (
    AlumniStoryCreateView,
    AlumniStoryDetailView,
    AlumniStoryListView,
    AlumniStorySuccessView,
)


urlpatterns = [
    path("alumni/", AlumniStoryListView.as_view(), name="alumni-list"),
    path("alumni/share/", AlumniStoryCreateView.as_view(), name="alumni-create"),
    path("alumni/thank-you/", AlumniStorySuccessView.as_view(), name="alumni-success"),
    path("alumni/<slug:slug>/", AlumniStoryDetailView.as_view(), name="alumni-detail"),
]
