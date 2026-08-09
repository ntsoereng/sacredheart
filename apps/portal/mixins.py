from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login


class StaffRequiredMixin(UserPassesTestMixin):

    raise_exception = True

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name(),
            )
        return super().handle_no_permission()

    def test_func(self):

        return (
            self.request.user.is_staff
            or
            self.request.user.is_superuser
        )


class StaffPermissionRequiredMixin(PermissionRequiredMixin, StaffRequiredMixin):
    raise_exception = True


class AnyStaffPermissionRequiredMixin(StaffPermissionRequiredMixin):
    """Allow a staff user when they hold at least one listed permission."""

    def has_permission(self):
        permissions = self.get_permission_required()
        return self.request.user.is_superuser or any(
            self.request.user.has_perm(permission) for permission in permissions
        )
