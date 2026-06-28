from django.views.generic import DetailView
from django.views.generic import ListView
from django.shortcuts import get_object_or_404

from .models import Post


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