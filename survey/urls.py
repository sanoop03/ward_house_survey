from django.urls import path
from .views import (
    HouseSurveyListCreateView,
    HouseSurveyDetailView,
    HousePhotoUploadView,
    HousePhotoDeleteView,
    FamilyMemberListCreateView,
    FamilyMemberDetailView,
    AdminFullReportView,
)

urlpatterns = [
    # House Survey
    path('houses/', HouseSurveyListCreateView.as_view(), name='house-list-create'),
    path('houses/<int:pk>/', HouseSurveyDetailView.as_view(), name='house-detail'),

    # House Photos (multiple angle images)
    path('houses/<int:pk>/photos/', HousePhotoUploadView.as_view(), name='house-photos'),
    path('photos/<int:pk>/', HousePhotoDeleteView.as_view(), name='photo-delete'),

    # Family Members
    path('houses/<int:pk>/family/', FamilyMemberListCreateView.as_view(), name='family-list-create'),
    path('family/<int:pk>/', FamilyMemberDetailView.as_view(), name='family-detail'),

    # Admin full report
    path('admin/report/', AdminFullReportView.as_view(), name='admin-report'),
]
