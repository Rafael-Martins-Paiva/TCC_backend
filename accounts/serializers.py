from rest_framework import serializers
from .models import User
from domain.accounts.aggregates.value_objects.email import Email, InvalidEmailError

class EmailField(serializers.Field):
    def to_internal_value(self, data):
        try:
            return Email(data)
        except InvalidEmailError as e:
            raise serializers.ValidationError(str(e))

    def to_representation(self, value: Email):
        return str(value)

class UserRegistrationSerializer(serializers.Serializer):
    
    email = EmailField()
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=False)

    def validate(self, attrs):
        if 'password2' in attrs and attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        return attrs

class EmailVerificationSerializer(serializers.Serializer):
    email = EmailField()
    token = serializers.CharField(max_length=255)

class ResendVerificationEmailSerializer(serializers.Serializer):
    email = EmailField()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"new_password": "As novas senhas não coincidem."})
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'bio')

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'bio', 'email')
        extra_kwargs = {
            'name': {'required': False},
            'bio': {'required': False},
        }

    def validate_email(self, value):
        raise serializers.ValidationError('Email cannot be updated.')

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
