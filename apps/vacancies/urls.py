from django.urls import path

from .views import VacancyDetailView, VacancyListView


urlpatterns = [
    path("vacancies/", VacancyListView.as_view(), name="vacancy-list"),
    path("vacancies/<slug:slug>/", VacancyDetailView.as_view(), name="vacancy-detail"),
]
