import json
from django.db import transaction
from rest_framework import serializers
from .models import HouseSurvey, HousePhoto, FamilyMember


# ─────────────────────────────────────────────
#  House Photo Serializer
# ─────────────────────────────────────────────

class HousePhotoSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = HousePhoto
        fields = ['id', 'house', 'photo', 'photo_url', 'caption', 'uploaded_at']
        read_only_fields = ['id', 'photo_url', 'uploaded_at']

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        elif obj.photo:
            return obj.photo.url
        return None


# ─────────────────────────────────────────────
#  Family Member Serializer
# ─────────────────────────────────────────────

class FamilyMemberSerializer(serializers.ModelSerializer):
    education = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='')
    occupation = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='')
    blood_group = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='')
    willing_to_donate_blood = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = FamilyMember
        fields = [
            'id', 'house', 'name', 'age', 'gender',
            'education', 'occupation', 'blood_group',
            'willing_to_donate_blood',
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'house': {'required': False},
        }

    def validate_education(self, val):
        return val or ''

    def validate_occupation(self, val):
        return val or ''

    def validate_blood_group(self, val):
        return val or ''


# ─────────────────────────────────────────────
#  Nested Section Serializers (Haritha Kerala Survey)
# ─────────────────────────────────────────────

class LocationSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=10, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=6, required=False, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='')


class HouseholdDetailsSerializer(serializers.Serializer):
    family_head_name = serializers.CharField(max_length=150)
    residence_name = serializers.CharField(max_length=150, required=False, allow_blank=True, allow_null=True, default='')
    residence_type = serializers.CharField(max_length=30, required=False, default='OWNED')
    house_name = serializers.CharField(max_length=150, required=False, allow_blank=True, allow_null=True, default='')
    house_number = serializers.CharField(max_length=50)
    house_number_type = serializers.CharField(max_length=20, required=False, default='NEW')
    phone_number = serializers.CharField(max_length=25, required=False, allow_blank=True, allow_null=True, default='')
    blood_group = serializers.CharField(max_length=10, required=False, allow_blank=True, allow_null=True, default='')
    age = serializers.IntegerField(required=False, allow_null=True)
    gender = serializers.CharField(max_length=10, required=False, allow_blank=True, allow_null=True, default='')
    education = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True, default='')
    occupation = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True, default='')
    willing_to_donate_blood = serializers.BooleanField(required=False, default=False)
    photo_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    location = LocationSerializer(required=False)


class RetiredGovEmployeeSerializer(serializers.Serializer):
    has_retired_employee = serializers.BooleanField(required=False, default=False)
    department = serializers.CharField(max_length=150, required=False, allow_blank=True, allow_null=True)
    sector = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    designation = serializers.CharField(max_length=150, required=False, allow_blank=True, allow_null=True)


class AgricultureSerializer(serializers.Serializer):
    currently_farming = serializers.BooleanField(required=False, default=False)
    interested_in_farming = serializers.BooleanField(required=False, default=False)


class WaterManagementSerializer(serializers.Serializer):
    water_sources = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list,
    )
    other_water_source = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    needs_pipeline_connection = serializers.BooleanField(required=False, default=False)


class WasteManagementSerializer(serializers.Serializer):
    organic_waste_method = serializers.CharField(max_length=50, required=False, allow_blank=True, default='BIOGAS')
    other_method = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    hands_over_non_organic_waste_to_haritha_karma_sena = serializers.BooleanField(required=False, default=False)


class GreenEnergySerializer(serializers.Serializer):
    has_solar = serializers.BooleanField(required=False, default=False)
    interested_in_installing_solar = serializers.BooleanField(required=False, default=False)
    has_ev = serializers.BooleanField(required=False, default=False)
    ev_vehicle_types = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list,
    )
    interested_in_ev = serializers.BooleanField(required=False, default=False)
    other_green_initiatives = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class HealthAccessibilitySerializer(serializers.Serializer):
    has_differently_abled_person = serializers.BooleanField(required=False, default=False)
    has_bedridden_patient = serializers.BooleanField(required=False, default=False)
    is_haritha_bhavan = serializers.BooleanField(required=False, default=False)
    interested_in_haritha_bhavan_scheme = serializers.BooleanField(required=False, default=False)
    uses_diapers = serializers.BooleanField(required=False, default=False)


class PropertyAndPublicSpacesSerializer(serializers.Serializer):
    has_vacant_public_land = serializers.BooleanField(required=False, default=False)
    public_land_location = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    public_land_photo_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    has_vacant_house_or_land_nearby = serializers.BooleanField(required=False, default=False)
    vacant_property_photo_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    vacant_property_location = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)

    is_waste_dumped_in_vacant_land = serializers.BooleanField(required=False, default=False)


class DomesticAnimalsSerializer(serializers.Serializer):
    has_animals = serializers.BooleanField(required=False, default=False)
    animals = serializers.DictField(
        child=serializers.IntegerField(min_value=0),
        required=False,
        default=dict,
    )


class EntrepreneurshipSerializer(serializers.Serializer):
    has_existing_business = serializers.BooleanField(required=False, default=False)
    interested_in_starting_home_business = serializers.BooleanField(required=False, default=False)
    business_details = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class AdditionalFeedbackSerializer(serializers.Serializer):
    suggestions = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class SurveyPayloadSerializer(serializers.Serializer):
    language = serializers.CharField(max_length=10, required=False, default='en')
    household_details = HouseholdDetailsSerializer(required=False)
    family_members = FamilyMemberSerializer(many=True, required=False)
    retired_government_employee = RetiredGovEmployeeSerializer(required=False)
    agriculture = AgricultureSerializer(required=False)
    water_management = WaterManagementSerializer(required=False)
    waste_management = WasteManagementSerializer(required=False)
    green_energy = GreenEnergySerializer(required=False)
    health_accessibility = HealthAccessibilitySerializer(required=False)
    property_and_public_spaces = PropertyAndPublicSpacesSerializer(required=False)
    domestic_animals = DomesticAnimalsSerializer(required=False)
    entrepreneurship = EntrepreneurshipSerializer(required=False)
    additional_feedback = AdditionalFeedbackSerializer(required=False)


# ─────────────────────────────────────────────
#  Helper: Convert HouseSurvey instance -> nested "survey" dict
# ─────────────────────────────────────────────

def build_survey_dict(obj):
    return {
        "language": obj.language,
        "household_details": {
            "family_head_name": obj.family_head_name,
            "residence_name": obj.residence_name,
            "residence_type": obj.residence_type,
            "house_name": obj.house_name,
            "house_number": obj.house_number,
            "house_number_type": obj.house_number_type,
            "phone_number": obj.phone_number,
            "blood_group": obj.blood_group,
            "age": obj.age,
            "gender": obj.gender,
            "education": obj.education,
            "occupation": obj.occupation,
            "willing_to_donate_blood": obj.willing_to_donate_blood,
            "photo_url": obj.photo_url,
            "location": {
                "latitude": float(obj.latitude) if obj.latitude is not None else None,
                "longitude": float(obj.longitude) if obj.longitude is not None else None,
                "address": obj.address,
            },
        },
        "family_members": [
            {
                "id": m.id,
                "name": m.name,
                "age": m.age,
                "gender": m.gender,
                "education": m.education,
                "occupation": m.occupation,
                "blood_group": m.blood_group,
                "willing_to_donate_blood": m.willing_to_donate_blood,
            }
            for m in obj.family_members.all()
        ],
        "retired_government_employee": {
            "has_retired_employee": obj.has_retired_employee,
            "department": obj.retired_department,
            "sector": obj.retired_sector,
            "designation": obj.retired_designation,
        },
        "agriculture": {
            "currently_farming": obj.currently_farming,
            "interested_in_farming": obj.interested_in_farming,
        },
        "water_management": {
            "water_sources": obj.water_sources or [],
            "other_water_source": obj.other_water_source,
            "needs_pipeline_connection": obj.needs_pipeline_connection,
        },
        "waste_management": {
            "organic_waste_method": obj.organic_waste_method,
            "other_method": obj.other_waste_method,
            "hands_over_non_organic_waste_to_haritha_karma_sena": obj.hands_over_non_organic_waste_to_haritha_karma_sena,
        },
        "green_energy": {
            "has_solar": obj.has_solar,
            "interested_in_installing_solar": obj.interested_in_installing_solar,
            "has_ev": obj.has_ev,
            "ev_vehicle_types": obj.ev_vehicle_types or [],
            "interested_in_ev": obj.interested_in_ev,
            "other_green_initiatives": obj.other_green_initiatives,
        },
        "health_accessibility": {
            "has_differently_abled_person": obj.has_differently_abled_person,
            "has_bedridden_patient": obj.has_bedridden_patient,
            "is_haritha_bhavan": obj.is_haritha_bhavan,
            "interested_in_haritha_bhavan_scheme": obj.interested_in_haritha_bhavan_scheme,
            "uses_diapers": obj.uses_diapers,
        },
        "property_and_public_spaces": {
            "has_vacant_public_land": obj.has_vacant_public_land,
            "public_land_location": obj.public_land_location,
            "public_land_photo_url": obj.public_land_photo_url,
            "has_vacant_house_or_land_nearby": obj.has_vacant_house_or_land_nearby,
            "vacant_property_photo_url": obj.vacant_property_photo_url,
            "vacant_property_location": obj.vacant_property_location,
            "is_waste_dumped_in_vacant_land": obj.is_waste_dumped_in_vacant_land,
        },
        "domestic_animals": {
            "has_animals": obj.has_animals,
            "animals": obj.animals or {"chicken": 0, "cow": 0, "goat": 0, "buffalo": 0},
        },
        "entrepreneurship": {
            "has_existing_business": obj.has_existing_business,
            "interested_in_starting_home_business": obj.interested_in_starting_home_business,
            "business_details": obj.business_details,
        },
        "additional_feedback": {
            "suggestions": obj.suggestions,
        },
    }


# ─────────────────────────────────────────────
#  House Survey — Summary List Serializer
# ─────────────────────────────────────────────

class HouseSurveyListSerializer(serializers.ModelSerializer):
    field_agent_name = serializers.CharField(source='field_agent.username', read_only=True)
    total_photos = serializers.SerializerMethodField()
    total_family_members = serializers.SerializerMethodField()
    survey = serializers.SerializerMethodField()

    class Meta:
        model = HouseSurvey
        fields = [
            'id',
            'house_number', 'house_number_type',
            'house_name', 'residence_name', 'residence_type',
            'family_head_name', 'phone_number', 'address',
            'field_agent_name',
            'total_photos', 'total_family_members',
            'survey',
            'created_at',
        ]

    def get_total_photos(self, obj):
        return obj.photos.count()

    def get_total_family_members(self, obj):
        return obj.family_members.count()

    def get_survey(self, obj):
        return build_survey_dict(obj)


# ─────────────────────────────────────────────
#  House Survey — Full Detail Serializer
# ─────────────────────────────────────────────

class HouseSurveyDetailSerializer(serializers.ModelSerializer):
    field_agent_name = serializers.CharField(source='field_agent.username', read_only=True)
    photos = HousePhotoSerializer(many=True, read_only=True)
    survey = serializers.SerializerMethodField()

    class Meta:
        model = HouseSurvey
        fields = [
            'id',
            'field_agent',
            'field_agent_name',
            'survey',
            'photos',
            'created_at',
            'updated_at',
        ]

    def get_survey(self, obj):
        return build_survey_dict(obj)


# ─────────────────────────────────────────────
#  House Survey — Create & Update Serializer
#  Accepts: {"survey": {...}} OR direct {...}
# ─────────────────────────────────────────────

class HouseSurveyCreateUpdateSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        # Support multipart form where 'survey' is a JSON string
        raw_survey = data.get('survey') if isinstance(data, dict) else None
        if isinstance(raw_survey, str):
            try:
                survey_data = json.loads(raw_survey)
            except json.JSONDecodeError as e:
                raise serializers.ValidationError({"survey": f"Invalid JSON string: {e}"})
            if isinstance(survey_data, dict) and 'survey' in survey_data and isinstance(survey_data['survey'], dict):
                survey_data = survey_data['survey']
        elif isinstance(raw_survey, dict):
            survey_data = raw_survey
        elif isinstance(data, dict):
            survey_data = data
        else:
            raise serializers.ValidationError({"survey": "Expected a JSON object."})

        partial = getattr(self, 'partial', False)
        if not partial and 'household_details' not in survey_data:
            raise serializers.ValidationError({
                "household_details": "This section is required inside 'survey'."
            })

        inner = SurveyPayloadSerializer(data=survey_data, partial=partial)
        inner.is_valid(raise_exception=True)
        return inner.validated_data

    def _apply_sections(self, instance, validated_data):
        if 'language' in validated_data:
            instance.language = validated_data['language']

        # 1. household_details
        hd = validated_data.get('household_details')
        if hd is not None:
            for field in [
                'family_head_name', 'residence_name', 'residence_type',
                'house_name', 'house_number', 'house_number_type',
                'phone_number', 'blood_group', 'age', 'gender',
                'education', 'occupation', 'willing_to_donate_blood', 'photo_url',
            ]:
                if field in hd:
                    val = hd[field]
                    if field in ('residence_name', 'house_name', 'phone_number', 'blood_group', 'gender', 'education', 'occupation') and val is None:
                        val = ''
                    setattr(instance, field, val)
            loc = hd.get('location')
            if loc is not None:
                if 'latitude' in loc:
                    instance.latitude = loc['latitude']
                if 'longitude' in loc:
                    instance.longitude = loc['longitude']
                if 'address' in loc:
                    instance.address = loc['address'] or ''

        # 3. retired_government_employee
        rge = validated_data.get('retired_government_employee')
        if rge is not None:
            if 'has_retired_employee' in rge:
                instance.has_retired_employee = rge['has_retired_employee']
            if 'department' in rge:
                instance.retired_department = rge['department']
            if 'sector' in rge:
                instance.retired_sector = rge['sector']
            if 'designation' in rge:
                instance.retired_designation = rge['designation']

        # 4. agriculture
        agr = validated_data.get('agriculture')
        if agr is not None:
            if 'currently_farming' in agr:
                instance.currently_farming = agr['currently_farming']
            if 'interested_in_farming' in agr:
                instance.interested_in_farming = agr['interested_in_farming']

        # 5. water_management
        wm = validated_data.get('water_management')
        if wm is not None:
            if 'water_sources' in wm:
                instance.water_sources = wm['water_sources']
            if 'other_water_source' in wm:
                instance.other_water_source = wm['other_water_source']
            if 'needs_pipeline_connection' in wm:
                instance.needs_pipeline_connection = wm['needs_pipeline_connection']

        # 6. waste_management
        waste = validated_data.get('waste_management')
        if waste is not None:
            if 'organic_waste_method' in waste:
                instance.organic_waste_method = waste['organic_waste_method'] or 'BIOGAS'
            if 'other_method' in waste:
                instance.other_waste_method = waste['other_method']
            if 'hands_over_non_organic_waste_to_haritha_karma_sena' in waste:
                instance.hands_over_non_organic_waste_to_haritha_karma_sena = (
                    waste['hands_over_non_organic_waste_to_haritha_karma_sena']
                )

        # 7. green_energy
        ge = validated_data.get('green_energy')
        if ge is not None:
            for f in ['has_solar', 'interested_in_installing_solar', 'has_ev', 'ev_vehicle_types', 'interested_in_ev', 'other_green_initiatives']:
                if f in ge:
                    setattr(instance, f, ge[f])

        # 8. health_accessibility
        ha = validated_data.get('health_accessibility')
        if ha is not None:
            for f in [
                'has_differently_abled_person', 'has_bedridden_patient',
                'is_haritha_bhavan', 'interested_in_haritha_bhavan_scheme', 'uses_diapers',
            ]:
                if f in ha:
                    setattr(instance, f, ha[f])

        # 9. property_and_public_spaces
        pps = validated_data.get('property_and_public_spaces')
        if pps is not None:
            for f in [
                'has_vacant_public_land', 'public_land_location', 'public_land_photo_url',
                'has_vacant_house_or_land_nearby', 'vacant_property_photo_url',
                'vacant_property_location', 'is_waste_dumped_in_vacant_land',
            ]:
                if f in pps:
                    setattr(instance, f, pps[f])

        # 10. domestic_animals
        da = validated_data.get('domestic_animals')
        if da is not None:
            if 'has_animals' in da:
                instance.has_animals = da['has_animals']
            if 'animals' in da:
                instance.animals = da['animals']

        # 11. entrepreneurship
        ent = validated_data.get('entrepreneurship')
        if ent is not None:
            for f in ['has_existing_business', 'interested_in_starting_home_business', 'business_details']:
                if f in ent:
                    setattr(instance, f, ent[f])

        # 12. additional_feedback
        fb = validated_data.get('additional_feedback')
        if fb is not None and 'suggestions' in fb:
            instance.suggestions = fb['suggestions']

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        instance = HouseSurvey(field_agent=user)
        self._apply_sections(instance, validated_data)
        instance.save()

        # 2. family_members
        members_data = validated_data.get('family_members', [])
        if members_data:
            members = [
                FamilyMember(
                    house=instance,
                    name=m['name'],
                    age=m['age'],
                    gender=m['gender'],
                    education=m.get('education') or '',
                    occupation=m.get('occupation') or '',
                    blood_group=m.get('blood_group') or '',
                    willing_to_donate_blood=m.get('willing_to_donate_blood', False),
                )
                for m in members_data
            ]
            FamilyMember.objects.bulk_create(members)

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        self._apply_sections(instance, validated_data)
        instance.save()

        # If family_members is explicitly included in update payload, replace them
        if 'family_members' in validated_data:
            instance.family_members.all().delete()
            members = [
                FamilyMember(
                    house=instance,
                    name=m['name'],
                    age=m['age'],
                    gender=m['gender'],
                    education=m.get('education') or '',
                    occupation=m.get('occupation') or '',
                    blood_group=m.get('blood_group') or '',
                    willing_to_donate_blood=m.get('willing_to_donate_blood', False),
                )
                for m in validated_data['family_members']
            ]
            FamilyMember.objects.bulk_create(members)

        return instance
