import hashlib
import hmac
import logging
import re
import uuid
from datetime import timedelta

from django.conf import settings
from django.core import signing
from django.db import IntegrityError, OperationalError, transaction
from django.shortcuts import render
from django.utils import timezone

from .models import PublicFormRateLimitBucket, PublicFormSubmissionToken


logger = logging.getLogger(__name__)
DEFAULT_TOKEN_MAX_AGE = 2 * 60 * 60
EMAIL_FIELD_NAMES = (
    "email",
    "parent_guardian_email",
    "verification_email",
)
PHONE_FIELD_NAMES = ("phone", "parent_phone_number")


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


def _normalize_email(value):
    return str(value or "").strip().casefold()


def _normalize_phone(value):
    return re.sub(r"\D+", "", str(value or ""))


def _identifier_hash(scope, kind, value):
    message = f"public-form:{scope}:{kind}:{value}".encode()
    return hmac.new(
        settings.SECRET_KEY.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()


def _record_attempt(identifier_hash, limit, window_seconds, now):
    for _attempt in range(3):
        try:
            with transaction.atomic():
                bucket = (
                    PublicFormRateLimitBucket.objects.select_for_update()
                    .filter(identifier_hash=identifier_hash)
                    .first()
                )
                if bucket is None:
                    PublicFormRateLimitBucket.objects.create(
                        identifier_hash=identifier_hash,
                        window_started_at=now,
                        attempts=1,
                    )
                    return False

                window_ends = bucket.window_started_at + timedelta(
                    seconds=window_seconds
                )
                if now >= window_ends:
                    bucket.window_started_at = now
                    bucket.attempts = 1
                else:
                    bucket.attempts += 1
                bucket.save(
                    update_fields=("window_started_at", "attempts", "updated_at")
                )
                return bucket.attempts > limit
        except IntegrityError:
            # Another process created the same bucket between SELECT and INSERT.
            continue
        except OperationalError:
            logger.exception("Public-form rate-limit storage was unavailable.")
            return True
    return True


def _form_identifiers(request):
    identifiers = [("ip", _client_address(request))]
    emails = {
        _normalize_email(request.POST.get(field_name))
        for field_name in EMAIL_FIELD_NAMES
    }
    phones = {
        _normalize_phone(request.POST.get(field_name))
        for field_name in PHONE_FIELD_NAMES
    }
    identifiers.extend(("email", value) for value in emails if value)
    identifiers.extend(("phone", value) for value in phones if value)
    return sorted(identifiers)


def _token_signer(scope):
    return signing.TimestampSigner(salt=f"public-form-submission:{scope}")


def create_public_form_token(scope):
    token_record = PublicFormSubmissionToken.objects.create(scope=scope)
    return _token_signer(scope).sign(str(token_record.token_id))


def _public_form_token_id(value, scope):
    max_age = getattr(
        settings,
        "PUBLIC_FORM_SUBMISSION_TOKEN_MAX_AGE",
        DEFAULT_TOKEN_MAX_AGE,
    )
    try:
        raw_token_id = _token_signer(scope).unsign(
            str(value or ""),
            max_age=max_age,
        )
        token_id = uuid.UUID(raw_token_id)
    except (signing.BadSignature, ValueError, TypeError):
        return None, max_age
    return token_id, max_age


def public_form_token_is_available(value, scope):
    token_id, max_age = _public_form_token_id(value, scope)
    if token_id is None:
        return False
    cutoff = timezone.now() - timedelta(seconds=max_age)
    return PublicFormSubmissionToken.objects.filter(
        token_id=token_id,
        scope=scope,
        consumed_at__isnull=True,
        created_at__gte=cutoff,
    ).exists()


def consume_public_form_token(value, scope):
    token_id, max_age = _public_form_token_id(value, scope)
    if token_id is None:
        return False
    cutoff = timezone.now() - timedelta(seconds=max_age)
    consumed = PublicFormSubmissionToken.objects.filter(
        token_id=token_id,
        scope=scope,
        consumed_at__isnull=True,
        created_at__gte=cutoff,
    ).update(consumed_at=timezone.now())
    return consumed == 1


class RateLimitMixin:
    """Apply a database-backed fixed-window limit to public POST endpoints."""

    rate_limit_count = 10
    rate_limit_window = 300
    rate_limit_scope = None
    rate_limit_error_template_name = "core/form_submission_error.html"

    @property
    def protection_scope(self):
        return self.rate_limit_scope or self.__class__.__name__

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST" and self._is_rate_limited(request):
            return self.rate_limit_response()
        return self.protected_dispatch(request, *args, **kwargs)

    def protected_dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def rate_limit_response(self):
        response = render(
            self.request,
            self.rate_limit_error_template_name,
            {
                "error_title": "Please wait before trying again",
                "error_message": (
                    "We have received too many attempts from these contact or "
                    "connection details. Please wait before trying again."
                ),
                "form_url": self.request.path,
            },
            status=429,
        )
        response["Retry-After"] = str(self.rate_limit_window)
        return response

    def _is_rate_limited(self, request):
        now = timezone.now()
        results = [
            _record_attempt(
                _identifier_hash(self.protection_scope, kind, value),
                self.rate_limit_count,
                self.rate_limit_window,
                now,
            )
            for kind, value in _form_identifiers(request)
        ]
        return any(results)


class PublicFormProtectionMixin(RateLimitMixin):
    """Add honeypot and atomic one-time-token checks to a public form view."""

    protection_error_template_name = "core/form_submission_error.html"

    def protected_dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            if request.POST.get("website", "").strip():
                return self.protection_error_response(
                    "We could not process this form",
                    "Please return to the form and try again.",
                    status=400,
                )
            if not public_form_token_is_available(
                request.POST.get("submission_token"),
                self.protection_scope,
            ):
                return self.invalid_submission_token_response()
        return super().protected_dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        if self.request.method == "GET":
            initial["submission_token"] = create_public_form_token(
                self.protection_scope
            )
        return initial

    def form_invalid(self, form):
        if "submission_token" in form.errors:
            return self.invalid_submission_token_response()
        return super().form_invalid(form)

    def form_valid(self, form):
        with transaction.atomic():
            if not consume_public_form_token(
                form.cleaned_data["submission_token"],
                self.protection_scope,
            ):
                return self.invalid_submission_token_response()
            return self.protected_form_valid(form)

    def protected_form_valid(self, form):
        return super().form_valid(form)

    def invalid_submission_token_response(self):
        return self.protection_error_response(
            "This form is no longer valid",
            (
                "The form may have expired or already been submitted. Open a "
                "fresh form before trying again."
            ),
            status=409,
        )

    def protection_error_response(self, title, message, status):
        return render(
            self.request,
            self.protection_error_template_name,
            {
                "error_title": title,
                "error_message": message,
                "form_url": self.request.path,
            },
            status=status,
        )
