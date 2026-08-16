import hashlib
import hmac
import logging
import re
import uuid
from datetime import timedelta

from django.conf import settings
from django.core import signing
from django.db import IntegrityError, OperationalError, transaction
from django.utils import timezone

from apps.core.throttling import _client_address

from .models import AdmissionRateLimitBucket, ApplicationSubmissionToken


logger = logging.getLogger(__name__)
TOKEN_SALT = "admissions.application-submission"
DEFAULT_TOKEN_MAX_AGE = 2 * 60 * 60
DEFAULT_RATE_LIMITS = {
    "ip": (20, 60 * 60),
    "email": (6, 60 * 60),
    "phone": (6, 60 * 60),
}


def normalize_guardian_email(value):
    return str(value or "").strip().casefold()


def normalize_guardian_phone(value):
    return re.sub(r"\D+", "", str(value or ""))


def _identifier_hash(kind, value):
    message = f"admissions:{kind}:{value}".encode()
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
                    AdmissionRateLimitBucket.objects.select_for_update()
                    .filter(identifier_hash=identifier_hash)
                    .first()
                )
                if bucket is None:
                    AdmissionRateLimitBucket.objects.create(
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
            # Another process created this bucket between SELECT and INSERT.
            continue
        except OperationalError:
            logger.exception("Admissions rate-limit storage was unavailable.")
            return True
    return True


def admission_attempt_is_limited(request):
    configured_limits = getattr(
        settings,
        "ADMISSIONS_RATE_LIMITS",
        DEFAULT_RATE_LIMITS,
    )
    identifiers = [("ip", _client_address(request))]
    email = normalize_guardian_email(request.POST.get("parent_guardian_email"))
    phone = normalize_guardian_phone(request.POST.get("parent_phone_number"))
    if email:
        identifiers.append(("email", email))
    if phone:
        identifiers.append(("phone", phone))

    now = timezone.now()
    results = []
    for kind, value in sorted(identifiers):
        limit, window_seconds = configured_limits.get(
            kind,
            DEFAULT_RATE_LIMITS[kind],
        )
        results.append(
            _record_attempt(
                _identifier_hash(kind, value),
                limit,
                window_seconds,
                now,
            )
        )
    return any(results)


def create_submission_token():
    token_record = ApplicationSubmissionToken.objects.create()
    return signing.TimestampSigner(salt=TOKEN_SALT).sign(str(token_record.token_id))


def _submission_token_id(value):
    max_age = getattr(
        settings,
        "ADMISSIONS_SUBMISSION_TOKEN_MAX_AGE",
        DEFAULT_TOKEN_MAX_AGE,
    )
    try:
        raw_token_id = signing.TimestampSigner(salt=TOKEN_SALT).unsign(
            str(value or ""),
            max_age=max_age,
        )
        token_id = uuid.UUID(raw_token_id)
    except (signing.BadSignature, ValueError, TypeError):
        return None, max_age
    return token_id, max_age


def submission_token_is_available(value):
    token_id, max_age = _submission_token_id(value)
    if token_id is None:
        return False
    cutoff = timezone.now() - timedelta(seconds=max_age)
    return ApplicationSubmissionToken.objects.filter(
        token_id=token_id,
        consumed_at__isnull=True,
        created_at__gte=cutoff,
    ).exists()


def consume_submission_token(value):
    token_id, max_age = _submission_token_id(value)
    if token_id is None:
        return False

    cutoff = timezone.now() - timedelta(seconds=max_age)
    consumed = ApplicationSubmissionToken.objects.filter(
        token_id=token_id,
        consumed_at__isnull=True,
        created_at__gte=cutoff,
    ).update(consumed_at=timezone.now())
    return consumed == 1
