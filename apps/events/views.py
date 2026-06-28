from django.views.generic import DetailView
from django.views.generic import ListView
from django.shortcuts import get_object_or_404

from .models import Event


class EventListView(ListView):

    model = Event

    template_name = "events/event_list.html"

    context_object_name = "events"

    paginate_by = 9

    queryset = (
        Event.objects
        .filter(is_published=True)
    )


class EventDetailView(DetailView):

    template_name = "events/event_detail.html"

    context_object_name = "event"

    def get_object(self):
        return get_object_or_404(
            Event,
            slug=self.kwargs["slug"],
            is_published=True,
        )