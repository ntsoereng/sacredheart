from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
from apps.posts.content import sanitize_post_html


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
        blank=True,
        max_length=2000,
        help_text=(
            "Paste the Google Maps embed URL or the complete iframe code from "
            "Share > Embed a map. Ordinary maps.app.goo.gl share links cannot be embedded."
        ),
    )

    facebook_url = models.URLField(
        blank=True,
        max_length=500,
        verbose_name="Facebook page URL",
    )

    instagram_url = models.URLField(
        blank=True,
        max_length=500,
        verbose_name="Instagram profile URL",
    )

    youtube_url = models.URLField(
        blank=True,
        max_length=500,
        verbose_name="YouTube channel URL",
    )

    tiktok_url = models.URLField(
        blank=True,
        max_length=500,
        verbose_name="TikTok profile URL",
    )

    x_url = models.URLField(
        blank=True,
        max_length=500,
        verbose_name="X (Twitter) profile URL",
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

    admissions_list = models.FileField(
        upload_to="admissions/lists/",
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        help_text="Upload the approved admissions list as a PDF when it is ready.",
    )

    prospectus = models.FileField(
        upload_to="admissions/prospectuses/",
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        help_text="Upload the current school prospectus as a PDF.",
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


class ExtracurricularActivity(models.Model):
    CATEGORY_CHOICES = (
        ("music", "Music and performance"),
        ("sport", "Sport"),
        ("academic", "Academic club"),
        ("service", "Service and leadership"),
        ("culture", "Culture and society"),
        ("other", "Other"),
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="other",
    )
    short_description = models.CharField(
        max_length=240,
        help_text="A short selling point shown on activity cards.",
    )
    description = models.TextField(
        help_text="Describe what the activity offers and how learners benefit.",
    )
    achievements = models.TextField(
        blank=True,
        help_text="Notable awards, performances or milestones. Enter one achievement per line.",
    )
    featured_image = models.ImageField(
        upload_to="activities/",
        blank=True,
        null=True,
        help_text="A wide, high-quality image works best.",
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Show this activity as a selling point on the homepage.",
    )
    is_published = models.BooleanField(
        default=True,
        help_text="Allow visitors to see this activity on the public website.",
    )
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("display_order", "name")
        verbose_name = "Club or activity"
        verbose_name_plural = "Clubs and activities"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "school-activity"
            slug = base_slug
            suffix = 2
            while (
                ExtracurricularActivity.objects
                .filter(slug=slug)
                .exclude(pk=self.pk)
                .exists()
            ):
                slug = f"{base_slug}-{suffix}"
                suffix += 1
            self.slug = slug
        self.description = sanitize_post_html(self.description)
        if self.achievements:
            self.achievements = sanitize_post_html(self.achievements)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
