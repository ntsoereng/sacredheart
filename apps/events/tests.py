from datetime import date, time
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Event


class CalendarViewTests(TestCase):
    calendar_url = reverse("event-list")

    @classmethod
    def setUpTestData(cls):
        cls.academic_event = Event.objects.create(
            title="Mock examinations begin",
            description="The examination timetable begins.",
            event_date=date(2026, 8, 10),
            start_time=time(8, 0),
            end_time=time(12, 30),
            category=Event.Category.ACADEMIC,
            location="Main Hall",
            featured=True,
            is_published=True,
        )
        cls.sport_event = Event.objects.create(
            title="Inter-school athletics",
            description="A school athletics meeting.",
            event_date=date(2026, 8, 15),
            category=Event.Category.SPORT,
            featured=True,
            is_published=True,
        )
        cls.multi_day_event = Event.objects.create(
            title="Admissions week",
            description="Admissions appointments throughout the week.",
            event_date=date(2026, 7, 30),
            end_date=date(2026, 8, 3),
            category=Event.Category.ADMISSIONS,
            is_published=True,
        )
        cls.unpublished_event = Event.objects.create(
            title="Draft staff meeting",
            description="This must not be public.",
            event_date=date(2026, 8, 20),
            category=Event.Category.MEETING,
            featured=True,
            is_published=False,
        )

    def test_calendar_uses_requested_month_and_preserves_filter_in_navigation(self):
        response = self.client.get(
            self.calendar_url,
            {"month": "2026-08", "category": "academic"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["month_start"], date(2026, 8, 1))
        self.assertContains(response, "August 2026")
        self.assertContains(response, "?month=2026-07&amp;category=academic")
        self.assertContains(response, "?month=2026-09&amp;category=academic")

    def test_category_filter_only_includes_matching_events(self):
        response = self.client.get(
            self.calendar_url,
            {"month": "2026-08", "category": "sport"},
        )

        self.assertContains(response, self.sport_event.title)
        self.assertNotContains(response, self.academic_event.title)
        self.assertEqual(response.context["active_category"], "sport")

    @patch("apps.events.views.timezone.localdate", return_value=date(2026, 8, 1))
    def test_unpublished_events_are_excluded_from_calendar_and_upcoming(self, _localdate):
        response = self.client.get(self.calendar_url, {"month": "2026-08"})

        self.assertNotContains(response, self.unpublished_event.title)
        self.assertNotIn(self.unpublished_event, response.context["upcoming_events"])

    def test_multi_day_event_is_attached_to_every_overlapping_day(self):
        response = self.client.get(self.calendar_url, {"month": "2026-08"})
        cells = {
            cell["date"]: cell
            for week in response.context["calendar_weeks"]
            for cell in week
        }

        for event_day in (
            date(2026, 7, 30),
            date(2026, 7, 31),
            date(2026, 8, 1),
            date(2026, 8, 2),
            date(2026, 8, 3),
        ):
            self.assertIn(self.multi_day_event, cells[event_day]["events"])
        self.assertNotIn(self.multi_day_event, cells[date(2026, 8, 4)]["events"])

    @patch("apps.events.views.timezone.localdate", return_value=date(2026, 8, 16))
    def test_upcoming_is_chronological_and_excludes_past_events(self, _localdate):
        ongoing = Event.objects.create(
            title="Ongoing school programme",
            description="Still underway.",
            event_date=date(2026, 8, 14),
            end_date=date(2026, 8, 17),
            featured=True,
        )
        future = Event.objects.create(
            title="Future important date",
            description="A later event.",
            event_date=date(2026, 8, 25),
            featured=True,
        )

        response = self.client.get(self.calendar_url, {"month": "2026-08"})
        upcoming = list(response.context["upcoming_events"])

        self.assertEqual(upcoming, [ongoing, future])
        self.assertNotIn(self.academic_event, upcoming)

    def test_calendar_download_contains_only_published_matching_events(self):
        response = self.client.get(reverse("calendar-download"), {"category": "academic"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/calendar; charset=utf-8")
        self.assertContains(response, self.academic_event.title)
        self.assertNotContains(response, self.sport_event.title)
        self.assertNotContains(response, self.unpublished_event.title)


class EventValidationTests(TestCase):
    def test_end_date_cannot_precede_start_date(self):
        event = Event(
            title="Invalid event",
            description="Invalid range.",
            event_date=date(2026, 8, 10),
            end_date=date(2026, 8, 9),
        )

        with self.assertRaisesMessage(ValidationError, "End date cannot be before the start date"):
            event.full_clean()
