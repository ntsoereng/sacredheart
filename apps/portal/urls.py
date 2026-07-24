from django.urls import path

from .views import (
    DashboardView,
    ApplicationListView,
    ApplicationDetailView,
    ApplicationExportView,
    MessageListView,
    MessageDetailView,
    AlumniReviewListView,
    AlumniReviewDetailView,
    ContentManagerView,
    EventCreateView,
    EventUpdateView,
    PostCreateView,
    PostUpdateView,
    StaffMemberCreateView,
    StaffMemberUpdateView,
    SubjectCreateView,
    SubjectUpdateView,
)

urlpatterns = [
    path(
        "",
        DashboardView.as_view(),
        name="dashboard",
    ),

    path(
        "applications/",
        ApplicationListView.as_view(),
        name="application-list",
    ),
    
    path(
        "applications/<int:pk>/",
        ApplicationDetailView.as_view(),
        name="application-detail",
    ),

    path(
        "applications/export/",
        ApplicationExportView.as_view(),
        name="application-export",
    ),

    path(
        "messages/",
        MessageListView.as_view(),
        name="message-list",
    ),

    path(
        "messages/<int:pk>/",
        MessageDetailView.as_view(),
        name="message-detail",
    ),
    path("alumni/", AlumniReviewListView.as_view(), name="alumni-review-list"),
    path("alumni/<int:pk>/", AlumniReviewDetailView.as_view(), name="alumni-review-detail"),
    path("content/", ContentManagerView.as_view(), name="content-manager"),
    path("content/posts/new/", PostCreateView.as_view(), name="post-create"),
    path("content/posts/<int:pk>/edit/", PostUpdateView.as_view(), name="post-edit"),
    path("content/events/new/", EventCreateView.as_view(), name="event-create"),
    path("content/events/<int:pk>/edit/", EventUpdateView.as_view(), name="event-edit"),
    path("content/subjects/new/", SubjectCreateView.as_view(), name="subject-create"),
    path("content/subjects/<int:pk>/edit/", SubjectUpdateView.as_view(), name="subject-edit"),
    path("content/staff/new/", StaffMemberCreateView.as_view(), name="staff-member-create"),
    path("content/staff/<int:pk>/edit/", StaffMemberUpdateView.as_view(), name="staff-member-edit"),
]
