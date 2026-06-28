from django.urls import path

from .views import (
    EventDetailView,
    EventListView,
)

urlpatterns = [
    path("events/", EventListView.as_view(),name="event-list"),
    path("events/<slug:slug>/", EventDetailView.as_view(), name="event-detail",)
]