import calendar
from datetime import datetime, timedelta

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.generic import DetailView, TemplateView

from .models import Event
from apps.core.seo import event_schema


FILTER_CATEGORIES = (
    ("", "All Events"),
    (Event.Category.ACADEMIC, "Academic"),
    (Event.Category.ADMISSIONS, "Admissions"),
    (Event.Category.SPORT, "Sport"),
    (Event.Category.HOLIDAY, "Holidays"),
)


def _selected_month(value):
    try:
        return datetime.strptime(value, "%Y-%m").date().replace(day=1)
    except (TypeError, ValueError):
        return timezone.localdate().replace(day=1)


def _next_month(first_day):
    return (first_day.replace(day=28) + timedelta(days=4)).replace(day=1)


def _active_category(value):
    filter_values = {key for key, _label in FILTER_CATEGORIES}
    return value if value in filter_values else ""


def _upcoming_filter(today):
    return Q(end_date__gte=today) | Q(end_date__isnull=True, event_date__gte=today)


class CalendarView(TemplateView):

    template_name = "events/event_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        month_start = _selected_month(self.request.GET.get("month"))
        active_category = _active_category(self.request.GET.get("category", ""))

        month_calendar = calendar.Calendar(firstweekday=calendar.MONDAY)
        weeks = month_calendar.monthdatescalendar(month_start.year, month_start.month)
        grid_start, grid_end = weeks[0][0], weeks[-1][-1]

        events = Event.objects.filter(
            is_published=True,
            event_date__lte=grid_end,
        ).filter(
            Q(end_date__gte=grid_start)
            | Q(end_date__isnull=True, event_date__gte=grid_start)
        )
        if active_category:
            events = events.filter(category=active_category)
        events = list(events.order_by("event_date", "start_time", "title"))

        events_by_day = {day: [] for week in weeks for day in week}
        for event in events:
            first = max(event.event_date, grid_start)
            last = min(event.last_date, grid_end)
            current = first
            while current <= last:
                events_by_day[current].append(event)
                current += timedelta(days=1)

        calendar_weeks = [
            [
                {
                    "date": day,
                    "events": events_by_day[day],
                    "is_current_month": day.month == month_start.month,
                    "is_today": day == today,
                }
                for day in week
            ]
            for week in weeks
        ]

        upcoming = Event.objects.filter(
            is_published=True,
            featured=True,
        ).filter(_upcoming_filter(today))
        if active_category:
            upcoming = upcoming.filter(category=active_category)

        planning_from = _next_month(max(month_start, today.replace(day=1)))
        plan_ahead = Event.objects.filter(
            is_published=True,
            featured=True,
            event_date__gte=planning_from,
        )
        if active_category:
            plan_ahead = plan_ahead.filter(category=active_category)

        previous_month = (month_start - timedelta(days=1)).replace(day=1)
        next_month = _next_month(month_start)
        category_suffix = f"&category={active_category}" if active_category else ""
        month_end = month_start.replace(
            day=calendar.monthrange(month_start.year, month_start.month)[1]
        )
        month_events = [
            event
            for event in events
            if event.event_date <= month_end and event.last_date >= month_start
        ]

        context.update(
            {
                "active_category": active_category,
                "calendar_weeks": calendar_weeks,
                "categories": FILTER_CATEGORIES,
                "category_suffix": category_suffix,
                "download_category_suffix": (
                    f"?category={active_category}" if active_category else ""
                ),
                "has_month_events": bool(month_events),
                "month_events": month_events,
                "month_start": month_start,
                "next_month": next_month,
                "plan_ahead": plan_ahead.order_by("event_date", "start_time")[:3],
                "previous_month": previous_month,
                "today": today,
                "today_month": today.replace(day=1),
                "upcoming_events": upcoming.order_by(
                    "event_date", "start_time", "title"
                )[:6],
            }
        )
        return context


def _ical_escape(value):
    return (
        str(value or "")
        .replace("\\", "\\\\")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
        .replace(",", "\\,")
        .replace(";", "\\;")
    )


def calendar_download(request):
    active_category = _active_category(request.GET.get("category", ""))
    events = Event.objects.filter(is_published=True).order_by(
        "event_date", "start_time", "title"
    )
    if active_category:
        events = events.filter(category=active_category)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Sacred Heart High School//School Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Sacred Heart High School",
    ]
    stamp = timezone.now().strftime("%Y%m%dT%H%M%SZ")
    for event in events:
        lines.extend(["BEGIN:VEVENT", f"UID:event-{event.pk}@sacredheart"])
        lines.append(f"DTSTAMP:{stamp}")
        if event.start_time:
            start = datetime.combine(event.event_date, event.start_time)
            lines.append(f"DTSTART;TZID=Africa/Maseru:{start:%Y%m%dT%H%M%S}")
            if event.end_time:
                end = datetime.combine(event.end_date or event.event_date, event.end_time)
                lines.append(f"DTEND;TZID=Africa/Maseru:{end:%Y%m%dT%H%M%S}")
        else:
            lines.append(f"DTSTART;VALUE=DATE:{event.event_date:%Y%m%d}")
            exclusive_end = event.last_date + timedelta(days=1)
            lines.append(f"DTEND;VALUE=DATE:{exclusive_end:%Y%m%d}")
        lines.extend(
            [
                f"SUMMARY:{_ical_escape(event.title)}",
                f"DESCRIPTION:{_ical_escape(strip_tags(event.description))}",
                f"LOCATION:{_ical_escape(event.location)}",
                f"URL:{request.build_absolute_uri(event.get_absolute_url())}",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")

    response = HttpResponse(
        "\r\n".join(lines) + "\r\n",
        content_type="text/calendar; charset=utf-8",
    )
    response["Content-Disposition"] = 'attachment; filename="sacred-heart-school-calendar.ics"'
    return response


class EventDetailView(DetailView):

    template_name = "events/event_detail.html"

    context_object_name = "event"

    def get_object(self):
        return get_object_or_404(
            Event,
            slug=self.kwargs["slug"],
            is_published=True,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["related_events"] = (
            Event.objects.filter(is_published=True)
            .exclude(pk=self.object.pk)[:3]
        )
        context["event_schema"] = event_schema(self.request, self.object)
        return context
