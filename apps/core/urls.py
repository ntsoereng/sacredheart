from django.urls import path
from .views import (
    AboutView,
    ContactView,
    DonationsView,
    HomeView,
    PrivacyPolicyView,
    SearchView,
    TermsOfUseView,
    favicon,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("favicon.ico", favicon, name="favicon"),
    path("about-us/", AboutView.as_view(), name="about-us"),
    path("donations/", DonationsView.as_view(), name="donations"),
    # path("test-404/", test_404, name="test-404"),
    path("search/", SearchView.as_view(), name="search"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("privacy/", PrivacyPolicyView.as_view(), name="privacy-policy"),
    path("terms/", TermsOfUseView.as_view(), name="terms-of-use"),
]
