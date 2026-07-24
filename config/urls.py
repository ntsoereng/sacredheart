from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.accounts.urls")),

    path("", include("apps.core.urls")),
    path("", include("apps.posts.urls")),
    path("", include("apps.events.urls")),
    path("", include("apps.academics.urls")),
    path("", include("apps.staff.urls")),
    path("", include("apps.admissions.urls")),
    path("", include("apps.alumni.urls")),
    path("dashboard/", include("apps.portal.urls")),
    path("", include("apps.pages.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
elif settings.SERVE_MEDIA:
    # Production fallback for Passenger/cPanel installations where Apache does
    # not map MEDIA_URL to MEDIA_ROOT. django.views.static.serve normalizes the
    # requested path and prevents traversal outside the configured media root.
    media_prefix = settings.MEDIA_URL.lstrip("/").rstrip("/")
    urlpatterns += [
        re_path(
            rf"^{media_prefix}/(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
