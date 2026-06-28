from django.urls import path

from .views import (
    PostDetailView,
    PostListView,
)

urlpatterns = [

    path(
        "news/",
        PostListView.as_view(),
        name="post-list",
    ),

    path(
        "news/<slug:slug>/",
        PostDetailView.as_view(),
        name="post-detail",
    ),
]