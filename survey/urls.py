from django.urls import path
from .views import (
    HouseSurveyListCreateView,
    HouseSurveyDetailView,
    StandalonePhotoUploadView,
    HousePhotoUploadView,
    HousePhotoDeleteView,
    FamilyMemberListCreateView,
    FamilyMemberDetailView,
    AdminFullReportView,
)

urlpatterns = [
    # Main Haritha Kerala Household Survey (GET list / POST create)
    path('houses/', HouseSurveyListCreateView.as_view(), name='house-list-create'),
    path('surveys/', HouseSurveyListCreateView.as_view(), name='survey-list-create'),
    path('submit/', HouseSurveyListCreateView.as_view(), name='survey-submit'),

    # Single Survey Detail / Update / Delete
    path('houses/<int:pk>/', HouseSurveyDetailView.as_view(), name='house-detail'),
    path('surveys/<int:pk>/', HouseSurveyDetailView.as_view(), name='survey-detail'),

    # Photo Uploads (standalone to get photo_url, or attached to a house)
    path('upload-photo/', StandalonePhotoUploadView.as_view(), name='standalone-photo-upload'),
    path('houses/<int:pk>/photos/', HousePhotoUploadView.as_view(), name='house-photos'),
    path('photos/<int:pk>/', HousePhotoDeleteView.as_view(), name='photo-delete'),

    # Family Members (can also be submitted inside POST /api/survey/houses/)
    path('houses/<int:pk>/family/', FamilyMemberListCreateView.as_view(), name='family-list-create'),
    path('family/<int:pk>/', FamilyMemberDetailView.as_view(), name='family-detail'),

    # Admin Full Report
    path('admin/report/', AdminFullReportView.as_view(), name='admin-report'),
]
