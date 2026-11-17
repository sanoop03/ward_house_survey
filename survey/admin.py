from django.contrib import admin
from .models import HouseSurvey, HousePhoto, FamilyMember


class HousePhotoInline(admin.TabularInline):
    model = HousePhoto
    extra = 0
    readonly_fields = ['uploaded_at']


class FamilyMemberInline(admin.TabularInline):
    model = FamilyMember
    extra = 0


@admin.register(HouseSurvey)
class HouseSurveyAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'house_number', 'house_name', 'family_head_name',
        'residence_type', 'phone_number', 'field_agent', 'created_at',
    ]
    list_filter = [
        'residence_type', 'house_number_type', 'currently_farming',
        'has_solar', 'has_ev', 'is_haritha_bhavan',
    ]
    search_fields = [
        'house_number', 'house_name', 'residence_name',
        'family_head_name', 'phone_number', 'address',
    ]
    readonly_fields = ['created_at', 'updated_at']
    inlines = [HousePhotoInline, FamilyMemberInline]
    ordering = ['-created_at']


@admin.register(HousePhoto)
class HousePhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'house', 'caption', 'uploaded_at']
    list_filter = ['uploaded_at']


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'age', 'gender', 'blood_group',
        'willing_to_donate_blood', 'education', 'occupation', 'house',
    ]
    list_filter = ['gender', 'blood_group', 'willing_to_donate_blood']
    search_fields = ['name', 'education', 'occupation']
