from rest_framework import serializers
from .models import User
from domain.accounts.aggregates.value_objects.email import Email, InvalidEmailError

class EmailField(serializers.Field):
    """Campo de serializer customizado para o Value Object Email."""
    def to_internal_value(self, data):
        """Transforma string de entrada em Value Object Email."""
        try:
            return Email(data)
        except InvalidEmailError as e:
            raise serializers.ValidationError(str(e))

    def to_representation(self, value: Email):
        """Transforma Value Object Email em string para a saída."""
        return str(value)

class UserRegistrationSerializer(serializers.Serializer):
    
    email = EmailField()
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
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
    """Serializer para retornar os dados do usuário."""
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'bio')

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer para validar os campos que o usuário pode atualizar."""
    class Meta:
        model = User
        # Lista de campos que o usuário PODE alterar.
        fields = ('first_name', 'last_name', 'bio', 'email')
        extra_kwargs = {
            # Garante que os campos são opcionais no PATCH
            'first_name': {'required': False},
            'last_name': {'required': False},
            'bio': {'required': False},
        }

    def validate_email(self, value):
        raise serializers.ValidationError('Email cannot be updated.')