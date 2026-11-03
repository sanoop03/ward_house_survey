from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser


# ─────────────────────────────────────────────
#  Admin Registration
# ─────────────────────────────────────────────

class AdminRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'confirm_password', 'phone', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(role=CustomUser.ROLE_ADMIN, **validated_data)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = False
        user.save()
        return user


# ─────────────────────────────────────────────
#  Field Agent Registration (Admin only)
# ─────────────────────────────────────────────

class FieldAgentRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'confirm_password', 'phone', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(role=CustomUser.ROLE_FIELD_AGENT, **validated_data)
        user.set_password(password)
        user.save()
        return user


# ─────────────────────────────────────────────
#  Login
# ─────────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise serializers.ValidationError("Your account has been deactivated. Contact admin.")
        attrs['user'] = user
        return attrs


# ─────────────────────────────────────────────
#  User Detail / Profile
# ─────────────────────────────────────────────

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'role', 'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'role', 'created_at']


# ─────────────────────────────────────────────
#  Field Agent list/detail (Admin view)
# ─────────────────────────────────────────────

class FieldAgentDetailSerializer(serializers.ModelSerializer):
    total_houses = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'role', 'is_active', 'created_at', 'total_houses',
        ]
        read_only_fields = fields

    def get_total_houses(self, obj):
        return obj.house_surveys.count()
