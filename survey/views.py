import base64
import uuid
from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import HouseSurvey, HousePhoto, FamilyMember
from .serializers import (
    HouseSurveyListSerializer,
    HouseSurveyDetailSerializer,
    HouseSurveyCreateUpdateSerializer,
    HousePhotoSerializer,
    FamilyMemberSerializer,
)
from accounts.permissions import IsAdminRole


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
            return HouseSurvey.objects.prefetch_related('photos', 'family_members').select_related('field_agent').get(pk=pk)
        else:
            return HouseSurvey.objects.prefetch_related('photos', 'family_members').select_related('field_agent').get(pk=pk, field_agent=user)
    except HouseSurvey.DoesNotExist:
        return None


def _save_base64_image(b64_str, house, caption, prefix):
    """Decode a data:image/...;base64,... string and save as HousePhoto."""
    try:
        if ';base64,' in b64_str:
            header, data = b64_str.split(';base64,', 1)
            ext = header.split('/')[-1].split(';')[0] or 'jpg'
        else:
            data = b64_str
            ext = 'jpg'
        decoded = base64.b64decode(data)
        filename = f"{prefix}_{uuid.uuid4().hex[:8]}.{ext}"
        photo_obj = HousePhoto(house=house, caption=caption)
        photo_obj.photo.save(filename, ContentFile(decoded), save=True)
        return photo_obj
    except Exception:
        return None


def attach_uploaded_files_to_house(request, house):
    """
    Supports both:
    1) Multipart files ('house_photo', 'public_land_photo', 'vacant_property_photo', or 'photos')
    2) Base64 image strings passed in photo_url, public_land_photo_url, or vacant_property_photo_url
    Saves files inside media/house_photos/<house_id>/ and sets absolute URLs on the HouseSurvey.
    """
    updated_fields = []

    # Handle Base64 strings (both 'data:image/...;base64,...' and raw Android Base64)
    for field_name, caption, prefix in [
        ('photo_url', 'House Photo', 'house'),
        ('public_land_photo_url', 'Public Land Photo', 'public_land'),
        ('vacant_property_photo_url', 'Vacant Property Photo', 'vacant_property'),
    ]:
        val = getattr(house, field_name, None)
        if isinstance(val, str) and val.strip() and not val.startswith(('http://', 'https://', '/media/')):
            p = _save_base64_image(val.strip(), house, caption, prefix)
            if p:
                setattr(house, field_name, request.build_absolute_uri(p.photo.url))
                updated_fields.append(field_name)

    # Handle multipart uploaded files
    if 'house_photo' in request.FILES:
        p = HousePhoto.objects.create(house=house, photo=request.FILES['house_photo'], caption='House Photo')
        house.photo_url = request.build_absolute_uri(p.photo.url)
        updated_fields.append('photo_url')

    if 'public_land_photo' in request.FILES:
        p = HousePhoto.objects.create(house=house, photo=request.FILES['public_land_photo'], caption='Public Land Photo')
        house.public_land_photo_url = request.build_absolute_uri(p.photo.url)
        updated_fields.append('public_land_photo_url')

    if 'vacant_property_photo' in request.FILES:
        p = HousePhoto.objects.create(house=house, photo=request.FILES['vacant_property_photo'], caption='Vacant Property Photo')
        house.vacant_property_photo_url = request.build_absolute_uri(p.photo.url)
        updated_fields.append('vacant_property_photo_url')

    photos = request.FILES.getlist('photos')
    captions = request.data.getlist('captions') if hasattr(request.data, 'getlist') else []
    for idx, photo_file in enumerate(photos):
        caption = captions[idx] if idx < len(captions) else 'House Photo'
        p = HousePhoto.objects.create(house=house, photo=photo_file, caption=caption)
        if idx == 0 and not house.photo_url:
            house.photo_url = request.build_absolute_uri(p.photo.url)
            updated_fields.append('photo_url')

    if updated_fields:
        house.save(update_fields=list(set(updated_fields)))


# ─────────────────────────────────────────────
#  Haritha Kerala Household Survey — List & Create
#  GET  /api/survey/houses/   (or /api/survey/surveys/) → Admin sees all; Agent sees own
#  POST /api/survey/houses/   (or /api/survey/surveys/) → Field Agent submits full survey
# ─────────────────────────────────────────────

class HouseSurveyListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        if request.user.role == 'admin':
            houses = HouseSurvey.objects.all().select_related('field_agent').prefetch_related('photos', 'family_members')
        else:
            houses = HouseSurvey.objects.filter(field_agent=request.user).select_related('field_agent').prefetch_related('photos', 'family_members')

        serializer = HouseSurveyListSerializer(houses, many=True, context={'request': request})
        return Response(
            {
                "count": houses.count(),
                "houses": serializer.data,
            }
        )

    def post(self, request):
        if request.user.role != 'field_agent':
            return Response(
                {"error": "Only field agents can submit house surveys."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = HouseSurveyCreateUpdateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            house = serializer.save()
            attach_uploaded_files_to_house(request, house)
            detail_serializer = HouseSurveyDetailSerializer(house, context={'request': request})
            return Response(
                {
                    "message": "Household survey submitted successfully.",
                    "id": house.id,
                    "house": detail_serializer.data,
                    "survey": detail_serializer.data['survey'],
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
#  House Survey — Detail, Update, Delete
#  GET    /api/survey/houses/<id>/
#  PATCH  /api/survey/houses/<id>/
#  PUT    /api/survey/houses/<id>/
#  DELETE /api/survey/houses/<id>/  (Admin only)
# ─────────────────────────────────────────────

class HouseSurveyDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request, pk):
        house = get_house_for_user(pk, request.user)
        if not house:
            return Response({"error": "House survey not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = HouseSurveyDetailSerializer(house, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, pk):
        return self._update(request, pk, partial=True)

    def put(self, request, pk):
        return self._update(request, pk, partial=True)

    def _update(self, request, pk, partial=True):
        house = get_house_for_user(pk, request.user)
        if not house:
            return Response({"error": "House survey not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == 'admin':
            return Response(
                {"error": "Admins cannot edit house surveys. Only the field agent who created it can."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = HouseSurveyCreateUpdateSerializer(
            house, data=request.data, partial=partial, context={'request': request}
        )
        if serializer.is_valid():
            house = serializer.save()
            attach_uploaded_files_to_house(request, house)
            detail_serializer = HouseSurveyDetailSerializer(house, context={'request': request})
            return Response(
                {
                    "message": "Household survey updated successfully.",
                    "id": house.id,
                    "house": detail_serializer.data,
                    "survey": detail_serializer.data['survey'],
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
#  Standalone Photo Upload (returns photo_url for JSON payload)
#  POST /api/survey/upload-photo/
# ─────────────────────────────────────────────

class StandalonePhotoUploadView(APIView):
    """
    Upload a photo before or during survey filling to get a full 'photo_url'
    (for household_details.photo_url, public_land_photo_url, or vacant_property_photo_url).
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        photo_file = request.FILES.get('photo') or (request.FILES.getlist('photos')[0] if request.FILES.getlist('photos') else None)
        if not photo_file:
            return Response({"error": "No image provided. Send file under key 'photo'."}, status=status.HTTP_400_BAD_REQUEST)

        caption = request.data.get('caption', 'Survey Photo')
        house_id = request.data.get('house_id')
        house = get_house_for_user(house_id, request.user) if house_id else None

        photo_obj = HousePhoto.objects.create(house=house, photo=photo_file, caption=caption)
        serializer = HousePhotoSerializer(photo_obj, context={'request': request})
        return Response(
            {
                "message": "Photo uploaded successfully.",
                "id": photo_obj.id,
                "photo_url": serializer.data['photo_url'],
                "caption": photo_obj.caption,
                "photo": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


# ─────────────────────────────────────────────
#  House Photos — Add & List multiple photos for a specific house
#  POST / GET /api/survey/houses/<id>/photos/
# ─────────────────────────────────────────────

class HousePhotoUploadView(APIView):
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
        if not photos and 'photo' in request.FILES:
            photos = [request.FILES['photo']]
        if not photos:
            return Response({"error": "No photos provided. Use key 'photos'."}, status=status.HTTP_400_BAD_REQUEST)

        captions = request.data.getlist('captions') if hasattr(request.data, 'getlist') else []
        created_photos = []
        for idx, photo_file in enumerate(photos):
            caption = captions[idx] if idx < len(captions) else ''
            photo_obj = HousePhoto.objects.create(house=house, photo=photo_file, caption=caption)
            created_photos.append(photo_obj)

        if not house.photo_url and created_photos:
            house.photo_url = request.build_absolute_uri(created_photos[0].photo.url)
            house.save(update_fields=['photo_url'])

        serializer = HousePhotoSerializer(created_photos, many=True, context={'request': request})
        return Response(
            {
                "message": f"{len(created_photos)} photo(s) uploaded successfully.",
                "photos": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def get(self, request, pk):
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

        if request.user.role == 'field_agent' and photo.house and photo.house.field_agent != request.user:
            return Response({"error": "You can only delete photos from your own surveys."}, status=status.HTTP_403_FORBIDDEN)

        photo.photo.delete(save=False)
        photo.delete()
        return Response({"message": "Photo deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# ─────────────────────────────────────────────
#  Family Members — Add & List
#  POST / GET /api/survey/houses/<id>/family/
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
#  Family Member — Detail, Update, Delete
#  GET / PATCH / DELETE /api/survey/family/<id>/
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
#  Admin: Full Report — all houses with full nested "survey" details
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
