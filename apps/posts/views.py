from django.views.generic import DetailView
from django.views.generic import ListView
from django.shortcuts import get_object_or_404

from .models import Post
from apps.core.seo import article_schema


class PostListView(ListView):

    model = Post

    template_name = "posts/post_list.html"

    context_object_name = "posts"

    paginate_by = 9

    queryset = (
        Post.objects
        .filter(is_published=True)
    )


class PostDetailView(DetailView):

    template_name = "posts/post_detail.html"

    context_object_name = "post"

    def get_object(self):
        return get_object_or_404(
            Post,
            slug=self.kwargs["slug"],
            is_published=True,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["related_posts"] = (
            Post.objects.filter(is_published=True)
            .exclude(pk=self.object.pk)[:3]
        )
        context["article_schema"] = article_schema(self.request, self.object)
        return context
