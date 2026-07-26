from unittest.mock import patch

from django.test import TestCase

from .content import sanitize_post_html
from .models import Post


class PostContentTests(TestCase):
    def test_browser_generated_bold_and_italic_markup_is_preserved(self):
        cleaned = sanitize_post_html("<p><b>Bold</b> and <i>italic</i></p>")

        self.assertIn("<b>Bold</b>", cleaned)
        self.assertIn("<i>italic</i>", cleaned)


class PostFeaturedImageTests(TestCase):
    def test_featured_image_webp_url_returns_candidate_when_available(self):
        post = Post(featured_image="posts/school-news.png")
        storage = post.featured_image.storage

        with patch.object(storage, "exists", return_value=True) as exists:
            with patch.object(storage, "url", return_value="/media/posts/school-news.webp"):
                self.assertEqual(
                    post.featured_image_webp_url,
                    "/media/posts/school-news.webp",
                )

        exists.assert_called_once_with("posts/school-news.webp")

    def test_featured_image_webp_url_is_empty_when_conversion_is_missing(self):
        post = Post(featured_image="posts/school-news.png")
        storage = post.featured_image.storage

        with patch.object(storage, "exists", return_value=False):
            self.assertEqual(post.featured_image_webp_url, "")

# Create your tests here.
