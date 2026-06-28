from django.urls import path
from .views import ContactView, HomeView, SearchView, test_404

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("test-404/", test_404, name="test-404"),
    path("search/", SearchView.as_view(), name="search"),
    path("contact/", ContactView.as_view(), name="contact"),
]