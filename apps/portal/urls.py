from . import workspace
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
    AlumniOpportunityReviewDetailView,
    AlumniOpportunityReviewListView,
    MentorshipRequestDetailView,
    MentorshipRequestListView,
    ActivityCreateView,
    ActivityUpdateView,
    AnnouncementUpdateView,
    ContentManagerView,
    EventCreateView,
    EventUpdateView,
    VacancyCreateView,
    VacancyUpdateView,
    PostCreateView,
    PostUpdateView,
    StaffMemberCreateView,
    StaffMemberUpdateView,
    SiteSettingsUpdateView,
    SubjectCreateView,
    SubjectUpdateView,
)

urlpatterns = [
    path("workspace/", workspace.workspace, name="workspace"),
    path("workspace/tasks/new/", workspace.task_form, name="workspace-task-new"),
    path("workspace/tasks/<int:pk>/", workspace.task_form, name="workspace-task"),
    path("workspace/tasks/<int:pk>/complete/", workspace.task_action, {"action": "complete"}, name="workspace-task-complete"),
    path("workspace/tasks/<int:pk>/reopen/", workspace.task_action, {"action": "reopen"}, name="workspace-task-reopen"),
    path("workspace/tasks/<int:pk>/delete/", workspace.task_action, {"action": "delete"}, name="workspace-task-delete"),

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
    path("alumni-opportunities/", AlumniOpportunityReviewListView.as_view(), name="alumni-opportunity-review-list"),
    path("alumni-opportunities/<int:pk>/", AlumniOpportunityReviewDetailView.as_view(), name="alumni-opportunity-review-detail"),
    path("mentorship-requests/", MentorshipRequestListView.as_view(), name="mentorship-request-list"),
    path("mentorship-requests/<int:pk>/", MentorshipRequestDetailView.as_view(), name="mentorship-request-detail"),
    path("content/", ContentManagerView.as_view(), name="content-manager"),
    path("settings/", SiteSettingsUpdateView.as_view(), name="site-settings"),
    path("content/announcement/edit/", AnnouncementUpdateView.as_view(), name="announcement-edit"),
    path("content/activities/new/", ActivityCreateView.as_view(), name="activity-create"),
    path("content/activities/<int:pk>/edit/", ActivityUpdateView.as_view(), name="activity-edit"),
    path("content/posts/new/", PostCreateView.as_view(), name="post-create"),
    path("content/posts/<int:pk>/edit/", PostUpdateView.as_view(), name="post-edit"),
    path("content/events/new/", EventCreateView.as_view(), name="event-create"),
    path("content/events/<int:pk>/edit/", EventUpdateView.as_view(), name="event-edit"),
    path("content/vacancies/new/", VacancyCreateView.as_view(), name="vacancy-create"),
    path("content/vacancies/<int:pk>/edit/", VacancyUpdateView.as_view(), name="vacancy-edit"),
    path("content/subjects/new/", SubjectCreateView.as_view(), name="subject-create"),
    path("content/subjects/<int:pk>/edit/", SubjectUpdateView.as_view(), name="subject-edit"),
    path("content/staff/new/", StaffMemberCreateView.as_view(), name="staff-member-create"),
    path("content/staff/<int:pk>/edit/", StaffMemberUpdateView.as_view(), name="staff-member-edit"),
]
