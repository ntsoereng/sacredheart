from django.urls import path
from .views import (
    AboutView,
    ActivityDetailView,
    ActivityListView,
    ContactView,
    DonationsView,
    HomeView,
    PrivacyPolicyView,
    SearchView,
    TermsOfUseView,
    favicon,
    robots_txt,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("favicon.ico", favicon, name="favicon"),
    path("robots.txt", robots_txt, name="robots-txt"),
    path("about-us/", AboutView.as_view(), name="about-us"),
    path("activities/", ActivityListView.as_view(), name="activity-list"),
    path("activities/<slug:slug>/", ActivityDetailView.as_view(), name="activity-detail"),
    path("donations/", DonationsView.as_view(), name="donations"),
    # path("test-404/", test_404, name="test-404"),
    path("search/", SearchView.as_view(), name="search"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("privacy/", PrivacyPolicyView.as_view(), name="privacy-policy"),
    path("terms/", TermsOfUseView.as_view(), name="terms-of-use"),
]
