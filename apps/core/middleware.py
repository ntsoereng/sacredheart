from django.conf import settings
from django.http import HttpResponseForbidden


class ScraperBlockingMiddleware:
    """Reject identified AI/data-harvesting crawlers without blocking search."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.blocked_agents = tuple(
            agent.lower() for agent in settings.BLOCKED_SCRAPER_USER_AGENTS
        )

    def __call__(self, request):
        user_agent = request.headers.get("user-agent", "").lower()
        if user_agent and any(agent in user_agent for agent in self.blocked_agents):
            return HttpResponseForbidden("Automated scraping is not permitted.")
        return self.get_response(request)


class PermissionsPolicyMiddleware:
    """Disable browser capabilities that this website does not use."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault("Permissions-Policy", settings.PERMISSIONS_POLICY)
        return response


class ResponseHeaderSanitizationMiddleware:
    """Remove optional response headers that disclose application technology."""

    identifying_headers = (
        "X-Powered-By",
        "X-AspNet-Version",
        "X-AspNetMvc-Version",
        "X-Generator",
        "X-Runtime",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        for header_name in self.identifying_headers:
            if header_name in response:
                del response[header_name]
        return response
