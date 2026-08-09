from django.conf import settings


class PermissionsPolicyMiddleware:
    """Disable browser capabilities that this website does not use."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault("Permissions-Policy", settings.PERMISSIONS_POLICY)
        return response
