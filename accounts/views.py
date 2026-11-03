from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token

from .models import CustomUser
from .serializers import (
    AdminRegisterSerializer,
    FieldAgentRegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    FieldAgentDetailSerializer,
)
from .permissions import IsAdminRole, IsFieldAgentRole


# ─────────────────────────────────────────────
#  Admin Registration
#  POST /api/auth/admin/register/
# ─────────────────────────────────────────────

class AdminRegisterView(APIView):
    """Register a new admin account (public — for first-time setup)."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "message": "Admin registered successfully.",
                    "token": token.key,
                    "user": UserProfileSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
#  Admin Login
#  POST /api/auth/admin/login/
# ─────────────────────────────────────────────

class AdminLoginView(APIView):
    """Login for admin users."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            if not user.is_admin:
                return Response(
                    {"error": "This account is not an admin account."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "message": "Admin login successful.",
                    "token": token.key,
                    "user": UserProfileSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
#  Field Agent Registration (Admin only)
#  POST /api/auth/agent/register/
# ─────────────────────────────────────────────

class FieldAgentRegisterView(APIView):
    """Admin creates a new field agent account."""
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request):
        serializer = FieldAgentRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "message": "Field agent registered successfully.",
                    "token": token.key,
                    "user": UserProfileSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
#  Field Agent Login
#  POST /api/auth/agent/login/
# ─────────────────────────────────────────────

class FieldAgentLoginView(APIView):
    """Login for field agents."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            if not user.is_field_agent:
                return Response(
                    {"error": "This account is not a field agent account."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "message": "Field agent login successful.",
                    "token": token.key,
                    "user": UserProfileSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
#  Logout
#  POST /api/auth/logout/
# ─────────────────────────────────────────────

class LogoutView(APIView):
    """Delete auth token (logout)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except Exception:
            pass
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────
#  My Profile
#  GET /api/auth/profile/
# ─────────────────────────────────────────────

class ProfileView(APIView):
    """Return the currently authenticated user's profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
#  Field Agent List (Admin only)
#  GET /api/auth/agents/
# ─────────────────────────────────────────────

class FieldAgentListView(APIView):
    """Admin: list all field agents."""
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        agents = CustomUser.objects.filter(role=CustomUser.ROLE_FIELD_AGENT).order_by('-created_at')
        serializer = FieldAgentDetailSerializer(agents, many=True)
        return Response(
            {
                "count": agents.count(),
                "agents": serializer.data,
            }
        )


# ─────────────────────────────────────────────
#  Field Agent Detail / Toggle / Delete (Admin)
#  GET    /api/auth/agents/<id>/
#  PATCH  /api/auth/agents/<id>/toggle-active/
#  DELETE /api/auth/agents/<id>/
# ─────────────────────────────────────────────

class FieldAgentDetailView(APIView):
    """Admin: get a specific field agent's detail."""
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_agent(self, pk):
        try:
            return CustomUser.objects.get(pk=pk, role=CustomUser.ROLE_FIELD_AGENT)
        except CustomUser.DoesNotExist:
            return None

    def get(self, request, pk):
        agent = self.get_agent(pk)
        if not agent:
            return Response({"error": "Field agent not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = FieldAgentDetailSerializer(agent)
        return Response(serializer.data)

    def delete(self, request, pk):
        agent = self.get_agent(pk)
        if not agent:
            return Response({"error": "Field agent not found."}, status=status.HTTP_404_NOT_FOUND)
        agent.delete()
        return Response({"message": "Field agent deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class ToggleAgentActiveView(APIView):
    """Admin: activate or deactivate a field agent."""
    permission_classes = [IsAuthenticated, IsAdminRole]

    def patch(self, request, pk):
        try:
            agent = CustomUser.objects.get(pk=pk, role=CustomUser.ROLE_FIELD_AGENT)
        except CustomUser.DoesNotExist:
            return Response({"error": "Field agent not found."}, status=status.HTTP_404_NOT_FOUND)

        agent.is_active = not agent.is_active
        agent.save(update_fields=['is_active'])

        # Also delete token so deactivated user is immediately logged out
        if not agent.is_active:
            Token.objects.filter(user=agent).delete()

        status_label = "activated" if agent.is_active else "deactivated"
        return Response(
            {
                "message": f"Field agent {status_label} successfully.",
                "is_active": agent.is_active,
                "agent_id": agent.id,
                "username": agent.username,
            }
        )
