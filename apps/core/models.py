from django.db import models


class SiteSettings(models.Model):

    school_name = models.CharField(
        max_length=200
    )

    tagline = models.CharField(
        max_length=300,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    phone = models.CharField(
        max_length=50,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    hero_title = models.CharField(
        max_length=255,
        blank=True
    )

    hero_subtitle = models.TextField(
        blank=True
    )

    hero_image = models.ImageField(
        upload_to="site/",
        blank=True,
        null=True
    )

    about_history = models.TextField(
        blank=True,
        help_text="The school history shown on the About Us page."
    )

    about_mission = models.TextField(
        blank=True,
        help_text="The mission statement shown on the About Us page."
    )

    about_vision = models.TextField(
        blank=True,
        help_text="The vision statement shown on the About Us page."
    )

    about_values = models.TextField(
        blank=True,
        help_text="The school values shown on the About Us page. Enter one value per line."
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    homepage_announcement = models.CharField(
        max_length=255,
        blank=True
    )

    show_announcement = models.BooleanField(
        default=False
    )

    office_hours = models.CharField(
        max_length=255,
        blank=True
)

    google_maps_embed_url = models.URLField(
        blank=True
    )
    
    logo = models.ImageField(
        upload_to="site/",
        blank=True,
        null=True
    )

    favicon = models.ImageField(
        upload_to="site/",
        blank=True,
        null=True
    )
    
    admissions_email = models.EmailField(
        blank=True
    )
    
    admissions_open = models.BooleanField(
        default=False,
        help_text="Controls whether online applications are being accepted."
    )

    admissions_message = models.TextField(
        blank=True,
        help_text="Message shown when admissions are closed."
    )

    def __str__(self):
        return self.school_name

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
        
        
        
class ContactMessage(models.Model):

    name = models.CharField(
        max_length=200
    )

    email = models.EmailField()

    subject = models.CharField(
        max_length=255
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_read = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.subject
