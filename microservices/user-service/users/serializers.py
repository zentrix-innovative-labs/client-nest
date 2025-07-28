from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address, validate_ipv6_address
from phonenumber_field.serializerfields import PhoneNumberField

from .models import User, UserActivity, UserSession
from profiles.models import UserProfile



# users/serializers.py
from rest_framework import serializers
from rest_framework.fields import ip_address_validators

class SafeIPAddressField(serializers.IPAddressField):
    def __init__(self, *args, **kwargs):
        validator = ip_address_validators(protocol=self.protocol, unpack_ipv4=self.unpack_ipv4)[0]
        super().__init__(*args, validators=[validator], **kwargs)

class IPAddressMixin:
    ip_address = SafeIPAddressField(required=False, allow_null=True)


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    phone_number = PhoneNumberField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'phone_number', 'password', 'password_confirm'
        )
        ref_name = "UserUser"
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': "Passwords don't match."
            })

        if not password:
            raise serializers.ValidationError({
                'password': "Password is required."
            })

        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')

        if not password:
            raise serializers.ValidationError("Password cannot be empty.")

        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )

            if not user:
                raise serializers.ValidationError(
                    'Unable to log in with provided credentials.',
                    code='authorization'
                )

            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled.',
                    code='authorization'
                )

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Must include "email" and "password".',
                code='authorization'
            )


class UserProfileSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField(required=False, allow_blank=True)
    profile_completeness = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField(source='get_full_name')

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'bio', 'profile_picture', 'phone_number',
            'is_verified', 'is_premium', 'privacy_level',
            'email_notifications', 'push_notifications',
            'timezone', 'language', 'created_at', 'updated_at',
            'profile_completeness'
        )
        read_only_fields = (
            'id', 'email', 'is_verified', 'is_premium',
            'created_at', 'updated_at'
        )

    def validate_username(self, value):
        user = self.instance
        if user and User.objects.filter(username=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField(source='get_full_name')

    class Meta:
        model = User
        fields = (
            'id', 'username', 'full_name', 'profile_picture',
            'is_verified', 'is_premium', 'created_at'
        )


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        style={'input_type': 'password'},
        required=True
    )
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        validators=[validate_password],
        required=True
    )
    new_password_confirm = serializers.CharField(
        style={'input_type': 'password'},
        required=True
    )

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        old_password = attrs.get('old_password')

        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': "New passwords don't match."
            })

        if old_password == new_password:
            raise serializers.ValidationError({
                'new_password': "New password must be different from the current password."
            })

        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        new_password = self.validated_data['new_password']

        if not new_password:
            raise serializers.ValidationError("New password cannot be empty.")

        user.set_password(new_password)
        user.save()
        return user


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("No active user found with this email address.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        validators=[validate_password],
        required=True
    )
    new_password_confirm = serializers.CharField(
        style={'input_type': 'password'},
        required=True
    )

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "Passwords don't match."
            })
        return attrs

    def save(self, user):
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserActivitySerializer(IPAddressMixin, serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = UserActivity
        fields = (
            'id', 'user_email', 'activity_type', 'ip_address',
            'user_agent', 'timestamp', 'details'
        )
        read_only_fields = ('id', 'timestamp')


class UserSessionSerializer(IPAddressMixin, serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = UserSession
        fields = (
            'id', 'user_email', 'session_key', 'ip_address',
            'user_agent', 'created_at', 'last_activity',
            'is_active', 'is_expired'
        )
        read_only_fields = (
            'id', 'session_key', 'created_at', 'last_activity'
        )


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Token is required.")
        return value


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value, is_active=True)
            if user.is_verified:
                raise serializers.ValidationError("This email is already verified.")
        except User.DoesNotExist:
            raise serializers.ValidationError("No active user found with this email address.")
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField(required=False, allow_blank=True)
    profile_completeness = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField(source='get_full_name')

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'bio', 'profile_picture', 'phone_number',
            'is_verified', 'is_premium', 'privacy_level',
            'email_notifications', 'push_notifications',
            'timezone', 'language', 'created_at', 'updated_at',
            'profile_completeness'
        )
        read_only_fields = (
            'id', 'email', 'is_verified', 'is_premium',
            'created_at', 'updated_at'
        )

    def validate_username(self, value):
        user = self.instance
        if user and User.objects.filter(username=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField(source='get_full_name')

    class Meta:
        model = User
        fields = (
            'id', 'username', 'full_name', 'profile_picture',
            'is_verified', 'is_premium', 'created_at'
        )


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(style={'input_type': 'password'}, required=True)
    new_password = serializers.CharField(style={'input_type': 'password'}, validators=[validate_password], required=True)
    new_password_confirm = serializers.CharField(style={'input_type': 'password'}, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "New passwords don't match."})
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({"new_password": "New password must be different from the old one."})
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("No active user found with this email address.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type': 'password'}, validators=[validate_password], required=True)
    new_password_confirm = serializers.CharField(style={'input_type': 'password'}, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Passwords don't match."})
        return attrs

    def save(self, user):
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserActivitySerializer(IPAddressMixin, serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = UserActivity
        fields = (
            'id', 'user_email', 'activity_type', 'ip_address',
            'user_agent', 'timestamp', 'details'
        )
        read_only_fields = ('id', 'timestamp')


class UserSessionSerializer(IPAddressMixin, serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = UserSession
        fields = (
            'id', 'user_email', 'session_key', 'ip_address',
            'user_agent', 'created_at', 'last_activity',
            'is_active', 'is_expired'
        )
        read_only_fields = (
            'id', 'session_key', 'created_at', 'last_activity'
        )


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Token is required.")
        return value


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value, is_active=True)
            if user.is_verified:
                raise serializers.ValidationError("This email is already verified.")
        except User.DoesNotExist:
            raise serializers.ValidationError("No active user found with this email address.")
        return value


class UserStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    verified_users = serializers.IntegerField()
    premium_users = serializers.IntegerField()
    active_sessions = serializers.IntegerField()
    recent_activities = serializers.IntegerField()

    class Meta:
        fields = (
            'total_users', 'verified_users', 'premium_users',
            'active_sessions', 'recent_activities'
        )
