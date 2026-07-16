from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = []

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.accounts.urls")),

    path("", include("apps.core.urls")),
    path("", include("apps.posts.urls")),
    path("", include("apps.events.urls")),
    path("", include("apps.academics.urls")),
    path("", include("apps.staff.urls")),
    path("", include("apps.admissions.urls")),
    path("dashboard/", include("apps.portal.urls")),
    path("", include("apps.pages.urls")),
]

# if settings.DEBUG:
#     urlpatterns += static(
#         settings.MEDIA_URL,
#         document_root=settings.MEDIA_ROOT
#     )
