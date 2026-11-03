from django.db import models
from django.conf import settings


# ─────────────────────────────────────────────
#  House Survey
# ─────────────────────────────────────────────

class HouseSurvey(models.Model):

    # Ownership choices
    OWNERSHIP_OWN = 'own'
    OWNERSHIP_RENT = 'rent'
    OWNERSHIP_LEASE = 'lease'
    OWNERSHIP_OTHERS = 'others'
    OWNERSHIP_CHOICES = [
        (OWNERSHIP_OWN, 'Own'),
        (OWNERSHIP_RENT, 'Rent'),
        (OWNERSHIP_LEASE, 'Lease'),
        (OWNERSHIP_OTHERS, 'Others'),
    ]

    # House type choices
    HOUSE_PERMANENT = 'permanent'
    HOUSE_SEMI_PERMANENT = 'semi_permanent'
    HOUSE_TEMPORARY = 'temporary'
    HOUSE_TYPE_CHOICES = [
        (HOUSE_PERMANENT, 'Permanent'),
        (HOUSE_SEMI_PERMANENT, 'Semi-Permanent'),
        (HOUSE_TEMPORARY, 'Temporary'),
    ]

    # Roof type choices
    ROOF_RCC = 'rcc'
    ROOF_TILES = 'tiles'
    ROOF_ASBESTOS = 'asbestos'
    ROOF_THATCHED = 'thatched'
    ROOF_OTHERS = 'others'
    ROOF_TYPE_CHOICES = [
        (ROOF_RCC, 'RCC'),
        (ROOF_TILES, 'Tiles'),
        (ROOF_ASBESTOS, 'Asbestos'),
        (ROOF_THATCHED, 'Thatched'),
        (ROOF_OTHERS, 'Others'),
    ]

    # Water source choices
    WATER_TAP = 'tap'
    WATER_WELL = 'well'
    WATER_BOREWELL = 'borewell'
    WATER_RIVER = 'river'
    WATER_OTHERS = 'others'
    WATER_SOURCE_CHOICES = [
        (WATER_TAP, 'Tap Water'),
        (WATER_WELL, 'Well'),
        (WATER_BOREWELL, 'Borewell'),
        (WATER_RIVER, 'River'),
        (WATER_OTHERS, 'Others'),
    ]

    # Electricity choices
    ELECTRICITY_YES = 'yes'
    ELECTRICITY_NO = 'no'
    ELECTRICITY_SOLAR = 'solar'
    ELECTRICITY_CHOICES = [
        (ELECTRICITY_YES, 'Yes'),
        (ELECTRICITY_NO, 'No'),
        (ELECTRICITY_SOLAR, 'Solar'),
    ]

    # Toilet choices
    TOILET_YES = 'yes'
    TOILET_NO = 'no'
    TOILET_SHARED = 'shared'
    TOILET_CHOICES = [
        (TOILET_YES, 'Yes (Private)'),
        (TOILET_NO, 'No'),
        (TOILET_SHARED, 'Shared'),
    ]

    # Ration card choices
    RATION_APL = 'apl'
    RATION_BPL = 'bpl'
    RATION_AAY = 'aay'
    RATION_NONE = 'none'
    RATION_CARD_CHOICES = [
        (RATION_APL, 'APL'),
        (RATION_BPL, 'BPL'),
        (RATION_AAY, 'AAY (Antyodaya)'),
        (RATION_NONE, 'None'),
    ]

    # ── Core Fields ──────────────────────────
    field_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='house_surveys',
        limit_choices_to={'role': 'field_agent'},
    )
    house_number = models.CharField(max_length=50)
    ward_no = models.CharField(max_length=20)
    address = models.TextField()
    landmark = models.CharField(max_length=255, blank=True, null=True)
    owner_name = models.CharField(max_length=100)

    # ── Choice Fields ─────────────────────────
    ownership = models.CharField(max_length=20, choices=OWNERSHIP_CHOICES)
    house_type = models.CharField(max_length=20, choices=HOUSE_TYPE_CHOICES)
    roof_type = models.CharField(max_length=20, choices=ROOF_TYPE_CHOICES)
    water_source = models.CharField(max_length=20, choices=WATER_SOURCE_CHOICES)
    electricity = models.CharField(max_length=10, choices=ELECTRICITY_CHOICES)
    toilet = models.CharField(max_length=10, choices=TOILET_CHOICES)
    ration_card_type = models.CharField(max_length=10, choices=RATION_CARD_CHOICES)

    # ── GPS Location ──────────────────────────
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="GPS latitude (e.g. 12.971598)"
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="GPS longitude (e.g. 77.594566)"
    )

    # ── Other ─────────────────────────────────
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'House Survey'
        verbose_name_plural = 'House Surveys'
        ordering = ['-created_at']

    def __str__(self):
        return f"House {self.house_number} | Ward {self.ward_no} | {self.owner_name}"


# ─────────────────────────────────────────────
#  House Photos (Multiple angle images)
#  Stored inside the project: media/house_photos/
# ─────────────────────────────────────────────

def house_photo_upload_path(instance, filename):
    """Organise photos per house: media/house_photos/<house_id>/<filename>"""
    return f"house_photos/{instance.house.id}/{filename}"


class HousePhoto(models.Model):
    house = models.ForeignKey(
        HouseSurvey,
        on_delete=models.CASCADE,
        related_name='photos',
    )
    photo = models.ImageField(
        upload_to=house_photo_upload_path,
        help_text="Multiple angle photo of the house",
    )
    caption = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="e.g. Front view, Back view, Left side, Right side",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'House Photo'
        verbose_name_plural = 'House Photos'
        ordering = ['uploaded_at']

    def __str__(self):
        return f"Photo of {self.house} — {self.caption or 'No caption'}"


# ─────────────────────────────────────────────
#  Family Member
# ─────────────────────────────────────────────

class FamilyMember(models.Model):

    RELATIONSHIP_HEAD = 'head'
    RELATIONSHIP_SPOUSE = 'spouse'
    RELATIONSHIP_SON = 'son'
    RELATIONSHIP_DAUGHTER = 'daughter'
    RELATIONSHIP_FATHER = 'father'
    RELATIONSHIP_MOTHER = 'mother'
    RELATIONSHIP_OTHERS = 'others'
    RELATIONSHIP_CHOICES = [
        (RELATIONSHIP_HEAD, 'Head of Family'),
        (RELATIONSHIP_SPOUSE, 'Spouse'),
        (RELATIONSHIP_SON, 'Son'),
        (RELATIONSHIP_DAUGHTER, 'Daughter'),
        (RELATIONSHIP_FATHER, 'Father'),
        (RELATIONSHIP_MOTHER, 'Mother'),
        (RELATIONSHIP_OTHERS, 'Others'),
    ]

    GENDER_MALE = 'male'
    GENDER_FEMALE = 'female'
    GENDER_OTHER = 'other'
    GENDER_CHOICES = [
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_OTHER, 'Other'),
    ]

    house = models.ForeignKey(
        HouseSurvey,
        on_delete=models.CASCADE,
        related_name='family_members',
    )
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    dob = models.DateField(help_text="Date of birth (YYYY-MM-DD)")
    age = models.PositiveIntegerField()
    education = models.CharField(max_length=100, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        verbose_name = 'Family Member'
        verbose_name_plural = 'Family Members'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_relationship_display()}) — {self.house}"
