from django.urls import path
from .views import AboutView, ContactView, DonationsView, HomeView, SearchView, test_404

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("about-us/", AboutView.as_view(), name="about-us"),
    path("donations/", DonationsView.as_view(), name="donations"),
    path("test-404/", test_404, name="test-404"),
    path("search/", SearchView.as_view(), name="search"),
    path("contact/", ContactView.as_view(), name="contact"),
]
