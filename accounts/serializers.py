from rest_framework import serializers
from domain.accounts.value_objects.email import Email, InvalidEmailError
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
    first_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        return attrs
