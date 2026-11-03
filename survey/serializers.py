from rest_framework import serializers
from .models import HouseSurvey, HousePhoto, FamilyMember


# ─────────────────────────────────────────────
#  House Photo Serializer
# ─────────────────────────────────────────────

class HousePhotoSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = HousePhoto
        fields = ['id', 'photo', 'photo_url', 'caption', 'uploaded_at']
        read_only_fields = ['id', 'photo_url', 'uploaded_at']

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return None


# ─────────────────────────────────────────────
#  Family Member Serializer
# ─────────────────────────────────────────────

class FamilyMemberSerializer(serializers.ModelSerializer):
    relationship_display = serializers.CharField(source='get_relationship_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)

    class Meta:
        model = FamilyMember
        fields = [
            'id', 'house', 'name', 'relationship', 'relationship_display',
            'gender', 'gender_display', 'dob', 'age',
            'education', 'occupation', 'phone',
        ]
        read_only_fields = ['id', 'relationship_display', 'gender_display']
        extra_kwargs = {
            'house': {'required': False},  # set via URL
        }


# ─────────────────────────────────────────────
#  House Survey — List (minimal)
# ─────────────────────────────────────────────

class HouseSurveyListSerializer(serializers.ModelSerializer):
    field_agent_name = serializers.CharField(source='field_agent.username', read_only=True)
    total_photos = serializers.SerializerMethodField()
    total_family_members = serializers.SerializerMethodField()

    class Meta:
        model = HouseSurvey
        fields = [
            'id', 'house_number', 'ward_no', 'address', 'owner_name',
            'ownership', 'house_type', 'field_agent_name',
            'total_photos', 'total_family_members', 'created_at',
        ]

    def get_total_photos(self, obj):
        return obj.photos.count()

    def get_total_family_members(self, obj):
        return obj.family_members.count()


# ─────────────────────────────────────────────
#  House Survey — Full Detail
# ─────────────────────────────────────────────

class HouseSurveyDetailSerializer(serializers.ModelSerializer):
    photos = HousePhotoSerializer(many=True, read_only=True)
    family_members = FamilyMemberSerializer(many=True, read_only=True)
    field_agent_name = serializers.CharField(source='field_agent.username', read_only=True)

    # Display values for choice fields
    ownership_display = serializers.CharField(source='get_ownership_display', read_only=True)
    house_type_display = serializers.CharField(source='get_house_type_display', read_only=True)
    roof_type_display = serializers.CharField(source='get_roof_type_display', read_only=True)
    water_source_display = serializers.CharField(source='get_water_source_display', read_only=True)
    electricity_display = serializers.CharField(source='get_electricity_display', read_only=True)
    toilet_display = serializers.CharField(source='get_toilet_display', read_only=True)
    ration_card_type_display = serializers.CharField(source='get_ration_card_type_display', read_only=True)

    class Meta:
        model = HouseSurvey
        fields = [
            'id',
            'field_agent', 'field_agent_name',
            'house_number', 'ward_no', 'address', 'landmark', 'owner_name',
            'ownership', 'ownership_display',
            'house_type', 'house_type_display',
            'roof_type', 'roof_type_display',
            'water_source', 'water_source_display',
            'electricity', 'electricity_display',
            'toilet', 'toilet_display',
            'ration_card_type', 'ration_card_type_display',
            'latitude', 'longitude',
            'remarks',
            'photos',
            'family_members',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'field_agent', 'field_agent_name',
            'ownership_display', 'house_type_display', 'roof_type_display',
            'water_source_display', 'electricity_display', 'toilet_display',
            'ration_card_type_display', 'photos', 'family_members',
            'created_at', 'updated_at',
        ]


# ─────────────────────────────────────────────
#  House Survey — Create / Update
# ─────────────────────────────────────────────

class HouseSurveyCreateSerializer(serializers.ModelSerializer):
    """Used for POST (create) and PUT/PATCH (update) by field agents."""

    class Meta:
        model = HouseSurvey
        fields = [
            'id',
            'house_number', 'ward_no', 'address', 'landmark', 'owner_name',
            'ownership', 'house_type', 'roof_type',
            'water_source', 'electricity', 'toilet', 'ration_card_type',
            'latitude', 'longitude',
            'remarks',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        # field_agent is set in the view from request.user
        validated_data['field_agent'] = self.context['request'].user
        return super().create(validated_data)
