import nh3
from django.utils.html import linebreaks


ALLOWED_POST_TAGS = {
    "a",
    "b",
    "blockquote",
    "br",
    "em",
    "h2",
    "h3",
    "i",
    "li",
    "ol",
    "p",
    "strong",
    "ul",
}


def sanitize_post_html(value):
    if "<" not in value:
        value = linebreaks(value)
    return nh3.clean(
        value,
        tags=ALLOWED_POST_TAGS,
        attributes={"a": {"href", "title", "target"}},
        url_schemes={"http", "https", "mailto"},
        link_rel="noopener noreferrer",
    )
