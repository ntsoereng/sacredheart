from django.test import TestCase

from .content import sanitize_post_html


class PostContentTests(TestCase):
    def test_browser_generated_bold_and_italic_markup_is_preserved(self):
        cleaned = sanitize_post_html("<p><b>Bold</b> and <i>italic</i></p>")

        self.assertIn("<b>Bold</b>", cleaned)
        self.assertIn("<i>italic</i>", cleaned)

# Create your tests here.
