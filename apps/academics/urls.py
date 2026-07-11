from django.urls import path

from .views import SubjectDetailView, SubjectListView


urlpatterns = [
    path("subjects/", SubjectListView.as_view(), name="subject-list"),
    path("subjects/<slug:slug>/", SubjectDetailView.as_view(), name="subject-detail"),
]
