from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError


class StaffAuthenticationForm(AuthenticationForm):
    """Authenticate only accounts that are permitted to use the staff portal."""

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise ValidationError(
                "This account does not have access to the staff portal.",
                code="staff_access_required",
            )
