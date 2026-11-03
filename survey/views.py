from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import HouseSurvey, HousePhoto, FamilyMember
from .serializers import (
    HouseSurveyListSerializer,
    HouseSurveyDetailSerializer,
    HouseSurveyCreateSerializer,
    HousePhotoSerializer,
    FamilyMemberSerializer,
)
from accounts.permissions import IsAdminRole, IsFieldAgentRole


# ─────────────────────────────────────────────
#  Helper: get house and enforce ownership
# ─────────────────────────────────────────────

def get_house_for_user(pk, user):
    """
    Return HouseSurvey if:
    - user is admin → any house
    - user is field_agent → only their own houses
    """
    try:
        if user.role == 'admin':
            return HouseSurvey.objects.get(pk=pk)
        else:
            return HouseSurvey.objects.get(pk=pk, field_agent=user)
    except HouseSurvey.DoesNotExist:
        return None


# ─────────────────────────────────────────────
#  House Survey List & Create
#  GET  /api/survey/houses/   → Admin sees all; Agent sees own
#  POST /api/survey/houses/   → Field Agent only
# ─────────────────────────────────────────────

class HouseSurveyListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        if request.user.role == 'admin':
            houses = HouseSurvey.objects.all().select_related('field_agent').prefetch_related('photos', 'family_members')
        else:
            houses = HouseSurvey.objects.filter(field_agent=request.user).select_related('field_agent').prefetch_related('photos', 'family_members')

        serializer = HouseSurveyListSerializer(houses, many=True)
        return Response(
            {
                "count": houses.count(),
                "houses": serializer.data,
            }
        )

    def post(self, request):
        # Only field agents can create surveys
        if request.user.role != 'field_agent':
            return Response(
                {"error": "Only field agents can submit house surveys."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = HouseSurveyCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            house = serializer.save()

            # Handle multiple photos uploaded along with the form
            photos = request.FILES.getlist('photos')
            captions = request.data.getlist('captions')
            for idx, photo_file in enumerate(photos):
                caption = captions[idx] if idx < len(captions) else ''
                HousePhoto.objects.create(house=house, photo=photo_file, caption=caption)

            detail_serializer = HouseSurveyDetailSerializer(house, context={'request': request})
            return Response(
                {
                    "message": "House survey submitted successfully.",
                    "house": detail_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
#  House Survey Detail, Update, Delete
#  GET    /api/survey/houses/<id>/
#  PATCH  /api/survey/houses/<id>/
#  DELETE /api/survey/houses/<id>/  (Admin only)
# ─────────────────────────────────────────────

class HouseSurveyDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, pk):
        house = get_house_for_user(pk, request.user)
        if not house:
            return Response({"error": "House survey not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = HouseSurveyDetailSerializer(house, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, pk):
        # Field agents can only update their own; Admin cannot create surveys
        house = get_house_for_user(pk, request.user)
        if not house:
            return Response({"error": "House survey not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == 'admin':
            return Response(
                {"error": "Admins cannot edit house surveys. Only the field agent who created it can."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = HouseSurveyCreateSerializer(
            house, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            detail_serializer = HouseSurveyDetailSerializer(house, context={'request': request})
            return Response(
                {
                    "message": "House survey updated successfully.",
                    "house": detail_serializer.data,
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user.role != 'admin':
            return Response(
                {"error": "Only admins can delete house surveys."},
                status=status.HTTP_403_FORBIDDEN,
            )
        house = get_house_for_user(pk, request.user)
        if not house:
            return Response({"error": "House survey not found."}, status=status.HTTP_404_NOT_FOUND)
        house.delete()
        return Response({"message": "House survey deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# ─────────────────────────────────────────────
#  House Photos — Add multiple angle photos
#  POST   /api/survey/houses/<id>/photos/
# ─────────────────────────────────────────────

class HousePhotoUploadView(APIView):
    """
    Upload one or more photos for a house survey.
    Send as multipart form-data with key 'photos' (multiple files)
    and optional 'captions' list.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        house = get_house_for_user(pk, request.user)
        if not house:
            return Response({"error": "House survey not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == 'admin':
            return Response(
                {"error": "Only the assigned field agent can add photos."},
                status=status.HTTP_403_FORBIDDEN,
            )

        photos = request.FILES.getlist('photos')
        if not photos:
            return Response({"error": "No photos provided. Use key 'photos'."}, status=status.HTTP_400_BAD_REQUEST)

        captions = request.data.getlist('captions')
        created_photos = []
        for idx, photo_file in enumerate(photos):
            caption = captions[idx] if idx < len(captions) else ''
            photo_obj = HousePhoto.objects.create(house=house, photo=photo_file, caption=caption)
            created_photos.append(photo_obj)

        serializer = HousePhotoSerializer(created_photos, many=True, context={'request': request})
        return Response(
            {
                "message": f"{len(created_photos)} photo(s) uploaded successfully.",
                "photos": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def get(self, request, pk):
        """List all photos for a house."""
        house = get_house_for_user(pk, request.user)
        if not house:
            return Response({"error": "House survey not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = HousePhotoSerializer(house.photos.all(), many=True, context={'request': request})
        return Response({"count": house.photos.count(), "photos": serializer.data})


# ─────────────────────────────────────────────
#  Single Photo Delete
#  DELETE /api/survey/photos/<id>/
# ─────────────────────────────────────────────

class HousePhotoDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            photo = HousePhoto.objects.select_related('house__field_agent').get(pk=pk)
        except HousePhoto.DoesNotExist:
            return Response({"error": "Photo not found."}, status=status.HTTP_404_NOT_FOUND)

        # Admin can delete any; agent can only delete their own house photos
        if request.user.role == 'field_agent' and photo.house.field_agent != request.user:
            return Response({"error": "You can only delete photos from your own surveys."}, status=status.HTTP_403_FORBIDDEN)

        # Delete file from disk too
        photo.photo.delete(save=False)
        photo.delete()
        return Response({"message": "Photo deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# ─────────────────────────────────────────────
#  Family Members — Add & List
#  POST /api/survey/houses/<id>/family/
#  GET  /api/survey/houses/<id>/family/
# ─────────────────────────────────────────────

class FamilyMemberListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        house = get_house_for_user(pk, request.user)
        if not house:
            return Response({"error": "House survey not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = FamilyMemberSerializer(house.family_members.all(), many=True)
        return Response({"count": house.family_members.count(), "family_members": serializer.data})

    def post(self, request, pk):
        if request.user.role == 'admin':
            return Response(
                {"error": "Only field agents can add family members."},
                status=status.HTTP_403_FORBIDDEN,
            )
        house = get_house_for_user(pk, request.user)
        if not house:
            return Response({"error": "House survey not found."}, status=status.HTTP_404_NOT_FOUND)

        # Support single member or bulk list
        many = isinstance(request.data, list)
        serializer = FamilyMemberSerializer(data=request.data, many=many)
        if serializer.is_valid():
            if many:
                members = [FamilyMember(house=house, **m) for m in serializer.validated_data]
                FamilyMember.objects.bulk_create(members)
                saved = FamilyMemberSerializer(house.family_members.all(), many=True)
            else:
                serializer.save(house=house)
                saved = serializer

            return Response(
                {
                    "message": "Family member(s) added successfully.",
                    "family_members": saved.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
#  Family Member Detail, Update, Delete
#  GET    /api/survey/family/<id>/
#  PATCH  /api/survey/family/<id>/
#  DELETE /api/survey/family/<id>/
# ─────────────────────────────────────────────

class FamilyMemberDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_member(self, pk, user):
        try:
            member = FamilyMember.objects.select_related('house__field_agent').get(pk=pk)
            if user.role == 'admin' or member.house.field_agent == user:
                return member
            return None
        except FamilyMember.DoesNotExist:
            return None

    def get(self, request, pk):
        member = self.get_member(pk, request.user)
        if not member:
            return Response({"error": "Family member not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(FamilyMemberSerializer(member).data)

    def patch(self, request, pk):
        if request.user.role == 'admin':
            return Response({"error": "Only field agents can edit family members."}, status=status.HTTP_403_FORBIDDEN)
        member = self.get_member(pk, request.user)
        if not member:
            return Response({"error": "Family member not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = FamilyMemberSerializer(member, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Family member updated.", "family_member": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        member = self.get_member(pk, request.user)
        if not member:
            return Response({"error": "Family member not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role == 'field_agent' and member.house.field_agent != request.user:
            return Response({"error": "You can only delete members from your own surveys."}, status=status.HTTP_403_FORBIDDEN)
        member.delete()
        return Response({"message": "Family member deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# ─────────────────────────────────────────────
#  Admin: Full Report — all houses with details
#  GET /api/survey/admin/report/
# ─────────────────────────────────────────────

class AdminFullReportView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        houses = HouseSurvey.objects.all().select_related('field_agent').prefetch_related('photos', 'family_members')
        serializer = HouseSurveyDetailSerializer(houses, many=True, context={'request': request})
        return Response(
            {
                "total_houses": houses.count(),
                "houses": serializer.data,
            }
        )
