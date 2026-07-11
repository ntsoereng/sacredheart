from django.test import TestCase
from django.urls import reverse


class AboutViewTests(TestCase):

    def test_about_page_is_available(self):
        response = self.client.get(reverse("about-us"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/about.html")
        self.assertContains(response, "OUR HISTORY")
        self.assertContains(response, "OUR MISSION")
        self.assertContains(response, "OUR VISION")
        self.assertContains(response, "OUR VALUES")


class DonationsViewTests(TestCase):

    def test_donations_page_is_available(self):
        response = self.client.get(reverse("donations"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/donations.html")
        self.assertContains(response, "Financial gifts")
        self.assertContains(response, "Useful items")
