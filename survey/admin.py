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
        'house_number', 'ward_no', 'owner_name', 'ownership',
        'house_type', 'field_agent', 'created_at'
    ]
    list_filter = ['ward_no', 'ownership', 'house_type', 'roof_type', 'ration_card_type']
    search_fields = ['house_number', 'owner_name', 'address', 'landmark']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [HousePhotoInline, FamilyMemberInline]
    ordering = ['-created_at']


@admin.register(HousePhoto)
class HousePhotoAdmin(admin.ModelAdmin):
    list_display = ['house', 'caption', 'uploaded_at']
    list_filter = ['uploaded_at']


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'relationship', 'gender', 'age', 'occupation', 'house']
    list_filter = ['relationship', 'gender', 'education']
    search_fields = ['name', 'phone']
