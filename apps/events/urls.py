from django.urls import path
from django.views.generic import RedirectView

from .views import (
    CalendarView,
    EventDetailView,
    calendar_download,
)

urlpatterns = [
    path("calendar/", CalendarView.as_view(), name="event-list"),
    path("calendar/download/", calendar_download, name="calendar-download"),
    path("events/", RedirectView.as_view(pattern_name="event-list", permanent=True), name="legacy-event-list"),
    path("events/<slug:slug>/", EventDetailView.as_view(), name="event-detail",)
]
