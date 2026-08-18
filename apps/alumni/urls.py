from django.urls import path

from .views import (
    AlumniActionSuccessView,
    AlumniOpportunityCreateView,
    AlumniOpportunityListView,
    AlumniStoryCreateView,
    AlumniStoryDetailView,
    AlumniStoryListView,
    AlumniStorySuccessView,
)


urlpatterns = [
    path("alumni/", AlumniStoryListView.as_view(), name="alumni-list"),
    path("alumni/share/", AlumniStoryCreateView.as_view(), name="alumni-create"),
    path("alumni/thank-you/", AlumniStorySuccessView.as_view(), name="alumni-success"),
    path("alumni/opportunities/share/", AlumniOpportunityCreateView.as_view(), name="alumni-opportunity-create"),
    path("alumni/opportunities/thank-you/", AlumniActionSuccessView.as_view(), name="alumni-opportunity-success"),
    path("alumni/opportunities/", AlumniOpportunityListView.as_view(), name="alumni-opportunity-list"),
    path("alumni/<slug:slug>/", AlumniStoryDetailView.as_view(), name="alumni-detail"),
]
