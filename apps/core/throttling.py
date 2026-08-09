import hashlib
import hmac

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse


def _client_address(request):
    """Return a client address without trusting spoofable forwarding headers."""
    remote_address = request.META.get("REMOTE_ADDR", "unknown")
    trusted_proxy_depth = settings.RATELIMIT_TRUSTED_PROXY_DEPTH
    if not trusted_proxy_depth:
        return remote_address

    forwarded = [
        address.strip()
        for address in request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")
        if address.strip()
    ]
    address_chain = forwarded + [remote_address]
    if len(address_chain) <= trusted_proxy_depth:
        return remote_address
    return address_chain[-(trusted_proxy_depth + 1)]


def _rate_limit_key(request, scope):
    value = f"{scope}:{_client_address(request)}"
    digest = hmac.new(
        settings.SECRET_KEY.encode(), value.encode(), hashlib.sha256
    ).hexdigest()
    return f"request-throttle:{digest}"


class RateLimitMixin:
    """Apply a fixed-window rate limit to anonymous-facing POST endpoints."""

    rate_limit_count = 10
    rate_limit_window = 300
    rate_limit_scope = None

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST" and self._is_rate_limited(request):
            response = HttpResponse(
                "Too many requests. Please wait and try again.",
                status=429,
                content_type="text/plain; charset=utf-8",
            )
            response["Retry-After"] = str(self.rate_limit_window)
            return response
        return super().dispatch(request, *args, **kwargs)

    def _is_rate_limited(self, request):
        scope = self.rate_limit_scope or self.__class__.__name__
        key = _rate_limit_key(request, scope)
        if cache.add(key, 1, timeout=self.rate_limit_window):
            return False
        try:
            attempts = cache.incr(key)
        except ValueError:
            cache.set(key, 1, timeout=self.rate_limit_window)
            return False
        return attempts > self.rate_limit_count
