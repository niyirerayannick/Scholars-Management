from django.db import models
from django.urls import reverse

from .status import is_active_replacement


class Scholar(models.Model):
    GENDER_CHOICES = [("Female", "Female"), ("Male", "Male"), ("Other", "Other")]
    STEM_CHOICES = [("STEM", "STEM"), ("Non-STEM", "Non-STEM")]
    LEVEL_CHOICES = [
        ("Bachelor", "Bachelor"),
        ("Masters", "Masters"),
        ("PhD", "PhD"),
        ("Diploma", "Diploma"),
        ("Certificate", "Certificate"),
    ]
    PROGRAM_CHOICES = [("Undergraduate", "Undergraduate"), ("Postgraduate", "Postgraduate")]

    student_no = models.CharField(max_length=60, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    category = models.CharField(max_length=80, blank=True)
    cohort = models.CharField(max_length=20)
    level_of_study = models.CharField(max_length=40, choices=LEVEL_CHOICES)
    campus = models.CharField(max_length=120)
    college = models.CharField(max_length=160)
    nationality = models.CharField(max_length=100)
    program_type = models.CharField(max_length=50, choices=PROGRAM_CHOICES, blank=True)
    program = models.CharField(max_length=200, blank=True)
    program_of_studies = models.CharField(max_length=220, blank=True)
    stem_category = models.CharField(max_length=30, choices=STEM_CHOICES, blank=True)
    is_active = models.BooleanField(default=True)
    is_alumni = models.BooleanField(default=False)
    consider_alumni_as_active = models.BooleanField(default=False)
    expected_graduation_year = models.PositiveIntegerField(null=True, blank=True)
    graduation_year = models.PositiveIntegerField(null=True, blank=True)
    class_year = models.CharField(max_length=20, blank=True)
    intake = models.CharField(max_length=60, blank=True)
    batch = models.CharField(max_length=80, blank=True)
    type_of_scholarship = models.CharField(max_length=120, blank=True)
    region_category = models.CharField(max_length=120, blank=True)
    home_country = models.CharField(max_length=120, blank=True)
    nationality_country = models.CharField(max_length=120, blank=True)
    province = models.CharField(max_length=120, blank=True)
    district = models.CharField(max_length=120, blank=True)
    sector = models.CharField(max_length=120, blank=True)
    cell = models.CharField(max_length=120, blank=True)
    village = models.CharField(max_length=120, blank=True)
    length_of_program = models.CharField(max_length=60, blank=True)
    home_district = models.CharField(max_length=120, blank=True)
    promotion = models.CharField(max_length=120, blank=True)
    accepted_offer_status = models.CharField(max_length=120, blank=True)
    dropout_active_status = models.CharField(max_length=120, blank=True)
    active_status_reason = models.TextField(blank=True)
    replacement = models.CharField(max_length=120, blank=True)
    by_enrollment = models.CharField(max_length=120, blank=True)
    alumni_status = models.CharField(max_length=120, blank=True)
    dob = models.DateField(null=True, blank=True)
    marital_status = models.CharField(max_length=60, blank=True)
    joining_year = models.PositiveIntegerField(null=True, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(unique=True)
    date_of_leaving_program = models.DateField(null=True, blank=True)
    where_is_going = models.CharField(max_length=200, blank=True)
    family_parent_1 = models.CharField(max_length=160, blank=True)
    family_parent_2 = models.CharField(max_length=160, blank=True)
    family_parent_3 = models.CharField(max_length=160, blank=True)
    family_parent_relation_1 = models.CharField(max_length=120, blank=True)
    family_parent_relation_2 = models.CharField(max_length=120, blank=True)
    family_parent_relation_3 = models.CharField(max_length=120, blank=True)
    family_parent_phone_1 = models.CharField(max_length=50, blank=True)
    family_parent_phone_2 = models.CharField(max_length=50, blank=True)
    family_parent_phone_3 = models.CharField(max_length=50, blank=True)
    life_status = models.CharField(max_length=160, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["cohort", "category", "gender"]),
            models.Index(fields=["campus", "college"]),
            models.Index(fields=["is_active", "is_alumni"]),
            models.Index(fields=["student_no"]),
            models.Index(fields=["type_of_scholarship"]),
        ]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def active_from_replacement(self):
        return is_active_replacement(self.replacement)

    @property
    def active_status_label(self):
        return "Active" if self.active_from_replacement else "Inactive"

    def get_absolute_url(self):
        return reverse("scholar_detail", kwargs={"pk": self.pk})
