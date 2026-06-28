from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from .models import Page


class PageDetailView(DetailView):

    template_name = "pages/page_detail.html"

    context_object_name = "page"

    def get_object(self):
        return get_object_or_404(
            Page,
            slug=self.kwargs["slug"],
            is_published=True,
        )