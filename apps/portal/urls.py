from django.urls import path

from .views import (
    DashboardView,
    ApplicationListView,
    ApplicationDetailView,
    ApplicationExportView,
    MessageListView,
    MessageDetailView,
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
]