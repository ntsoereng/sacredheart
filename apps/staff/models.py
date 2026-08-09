from django.core.exceptions import ValidationError
from django.db import models
from apps.posts.content import sanitize_post_html


class StaffMember(models.Model):
    full_name = models.CharField(max_length=200)
    role = models.CharField(max_length=150, default="Teacher")
    profile_picture = models.ImageField(upload_to="staff/", blank=True, null=True)
    short_bio = models.TextField()
    motto = models.CharField(max_length=255, blank=True)
    started_at_shhs = models.DateField(blank=True, null=True)
    subjects = models.ManyToManyField(
        "academics.Subject",
        blank=True,
        related_name="teachers",
        help_text="Optional: select the subjects this staff member teaches.",
    )
    is_principal = models.BooleanField(default=False)
    welcome_remarks = models.TextField(
        blank=True,
        help_text="Shown in the principal's welcome section.",
    )
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-is_principal", "display_order", "full_name")

    def clean(self):
        if self.is_principal and not self.welcome_remarks:
            raise ValidationError(
                {"welcome_remarks": "Please add the principal's welcome remarks."}
            )
        if (
            self.is_principal
            and StaffMember.objects.filter(is_principal=True)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError(
                {"is_principal": "Another staff member is already the principal."}
            )

    def save(self, *args, **kwargs):
        self.short_bio = sanitize_post_html(self.short_bio)
        if self.welcome_remarks:
            self.welcome_remarks = sanitize_post_html(self.welcome_remarks)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} — {self.role}"
