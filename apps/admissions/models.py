from django.db import models


class Application(models.Model):

    DISTRICT_CHOICES = [
        ("Berea", "Berea"),
        ("Butha-Buthe", "Butha-Buthe"),
        ("Leribe", "Leribe"),
        ("Mafeteng", "Mafeteng"),
        ("Maseru", "Maseru"),
        ("Mohale's Hoek", "Mohale's Hoek"),
        ("Mokhotlong", "Mokhotlong"),
        ("Qacha's Nek", "Qacha's Nek"),
        ("Quthing", "Quthing"),
        ("Thaba-Tseka", "Thaba-Tseka"),
    ]
    
    STATUS_CHOICES = [
        ("new", "New"),
        ("review", "Under Review"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
    ]

    academic_year = models.CharField(
        max_length=10
    )

    student_name = models.CharField(
        max_length=100
    )

    student_surname = models.CharField(
        max_length=100
    )

    date_of_birth = models.DateField()

    parent_guardian_names = models.CharField(
        max_length=255
    )

    parent_phone_number = models.CharField(
        max_length=30
    )

    home_address = models.TextField()

    previous_school = models.CharField(
        max_length=255
    )

    district = models.CharField(
        max_length=50,
        choices=DISTRICT_CHOICES
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    reviewed = models.BooleanField(
        default=False
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
    )

    notes = models.TextField(
        blank=True
    )
    
    reference_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return (
            f"{self.academic_year} "
            f"{self.student_name} "
            f"{self.student_surname}"
        )
    
    def save(self, *args, **kwargs):

        creating = self.pk is None

        super().save(*args, **kwargs)

        if creating and not self.reference_number:

            self.reference_number = (
                f"SHHS-{self.academic_year}-{self.pk:05d}"
            )

            super().save(
                update_fields=["reference_number"]
            )