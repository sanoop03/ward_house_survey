from django.db import models
from django.conf import settings


# ─────────────────────────────────────────────
#  Haritha Kerala Household Survey (Main Model)
# ─────────────────────────────────────────────

def survey_photo_upload_path(instance, filename):
    """Store standalone uploaded survey photos inside media/house_photos/uploads/"""
    return f"house_photos/uploads/{filename}"


class HouseSurvey(models.Model):
    # Role relationship
    field_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='house_surveys',
        limit_choices_to={'role': 'field_agent'},
    )

    # Top-level survey metadata
    language = models.CharField(max_length=10, default='en')

    # ── 1. Household Details (household_details) ──
    family_head_name = models.CharField(max_length=150)
    residence_name = models.CharField(max_length=150, blank=True, default='')
    residence_type = models.CharField(max_length=30, default='OWNED')  # OWNED, RENTED, etc.
    house_name = models.CharField(max_length=150, blank=True, default='')
    house_number = models.CharField(max_length=50)
    house_number_type = models.CharField(max_length=20, default='NEW')  # NEW, OLD
    phone_number = models.CharField(max_length=25, blank=True, default='')
    blood_group = models.CharField(max_length=10, blank=True, default='')
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True, default='')  # M, F, T
    education = models.CharField(max_length=100, blank=True, default='')
    occupation = models.CharField(max_length=100, blank=True, default='')
    willing_to_donate_blood = models.BooleanField(default=False)
    photo_url = models.URLField(max_length=500, blank=True, null=True)

    # Location (household_details.location)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    address = models.TextField(blank=True, default='')

    # ── 3. Retired Government Employee (retired_government_employee) ──
    has_retired_employee = models.BooleanField(default=False)
    retired_department = models.CharField(max_length=150, blank=True, null=True)
    retired_sector = models.CharField(max_length=50, blank=True, null=True)  # GOVERNMENT, PSU
    retired_designation = models.CharField(max_length=150, blank=True, null=True)

    # ── 4. Agriculture (agriculture) ──
    currently_farming = models.BooleanField(default=False)
    interested_in_farming = models.BooleanField(default=False)

    # ── 5. Water Management (water_management) ──
    water_sources = models.JSONField(default=list, blank=True)  # ["WELL", "WATER_AUTHORITY", "NEIGHBOUR_WELL", "OTHER"]
    other_water_source = models.CharField(max_length=255, blank=True, null=True)
    needs_pipeline_connection = models.BooleanField(default=False)

    # ── 6. Waste Management (waste_management) ──
    organic_waste_method = models.CharField(max_length=50, blank=True, default='BIOGAS')  # BIOGAS, RING_COMPOST, BIO_BIN, OTHER
    other_waste_method = models.CharField(max_length=255, blank=True, null=True)
    hands_over_non_organic_waste_to_haritha_karma_sena = models.BooleanField(default=False)

    # ── 7. Green Energy & EV Vehicles (green_energy) ──
    has_solar = models.BooleanField(default=False)
    interested_in_installing_solar = models.BooleanField(default=False)
    has_ev = models.BooleanField(default=False)
    ev_vehicle_types = models.JSONField(default=list, blank=True)  # ["TWO_WHEELER", "THREE_WHEELER", "FOUR_WHEELER"]
    interested_in_ev = models.BooleanField(default=False)
    other_green_initiatives = models.TextField(blank=True, null=True)

    # ── 8. Health & Accessibility (health_accessibility) ──
    has_differently_abled_person = models.BooleanField(default=False)
    has_bedridden_patient = models.BooleanField(default=False)
    is_haritha_bhavan = models.BooleanField(default=False)
    interested_in_haritha_bhavan_scheme = models.BooleanField(default=False)
    uses_diapers = models.BooleanField(default=False)

    # ── 9. Property & Public Spaces (property_and_public_spaces) ──
    has_vacant_public_land = models.BooleanField(default=False)
    public_land_location = models.CharField(max_length=255, blank=True, null=True)
    public_land_photo_url = models.URLField(max_length=500, blank=True, null=True)

    has_vacant_house_or_land_nearby = models.BooleanField(default=False)
    vacant_property_photo_url = models.URLField(max_length=500, blank=True, null=True)
    vacant_property_location = models.CharField(max_length=255, blank=True, null=True)

    is_waste_dumped_in_vacant_land = models.BooleanField(default=False)

    # ── 10. Domestic Animals (domestic_animals) ──
    has_animals = models.BooleanField(default=False)
    animals = models.JSONField(
        default=dict,
        blank=True,
        help_text='e.g. {"chicken": 10, "cow": 2, "goat": 3, "buffalo": 0}',
    )

    # ── 11. Entrepreneurship (entrepreneurship) ──
    has_existing_business = models.BooleanField(default=False)
    interested_in_starting_home_business = models.BooleanField(default=False)
    business_details = models.TextField(blank=True, null=True)

    # ── 12. Additional Feedback (additional_feedback) ──
    suggestions = models.TextField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'House Survey'
        verbose_name_plural = 'House Surveys'
        ordering = ['-created_at']

    def __str__(self):
        return f"House {self.house_number} ({self.house_name or self.residence_name}) | {self.family_head_name}"


# ─────────────────────────────────────────────
#  House Photos (Stored inside media/house_photos/<house_id>/)
# ─────────────────────────────────────────────

def house_photo_upload_path(instance, filename):
    """Organise photos per house: media/house_photos/<house_id>/<filename>"""
    folder = instance.house.id if instance.house_id else 'general'
    return f"house_photos/{folder}/{filename}"


class HousePhoto(models.Model):
    house = models.ForeignKey(
        HouseSurvey,
        on_delete=models.CASCADE,
        related_name='photos',
        null=True,
        blank=True,
    )
    photo = models.ImageField(
        upload_to=house_photo_upload_path,
        help_text="Uploaded photo (house, public land, or vacant property)",
    )
    caption = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="e.g. House Photo, Public Land, Vacant Property, Front View",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'House Photo'
        verbose_name_plural = 'House Photos'
        ordering = ['uploaded_at']

    def __str__(self):
        return f"Photo #{self.id} ({self.caption or 'No caption'})"


# ─────────────────────────────────────────────
#  2. Family Member (family_members[])
# ─────────────────────────────────────────────

class FamilyMember(models.Model):
    house = models.ForeignKey(
        HouseSurvey,
        on_delete=models.CASCADE,
        related_name='family_members',
    )
    name = models.CharField(max_length=150)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10)  # M, F, T
    education = models.CharField(max_length=100, blank=True, default='')
    occupation = models.CharField(max_length=100, blank=True, default='')
    blood_group = models.CharField(max_length=10, blank=True, default='')
    willing_to_donate_blood = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Family Member'
        verbose_name_plural = 'Family Members'
        ordering = ['id']

    def __str__(self):
        return f"{self.name} ({self.age}, {self.gender}) — House #{self.house_id}"
