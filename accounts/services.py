from django.contrib.auth import get_user_model
User = get_user_model()
class UserService:
    def create_user(self, user_data: dict) -> User:
        """
        Cria um novo usuário no sistema usando o CustomUserManager.
        """
        
        password = user_data.pop('password')
        email = user_data.pop('email')
        
        
        
        user_data.pop('password2', None)
        
        
        user = User.objects.create_user(email=email, password=password, **user_data)
        
        return user
