import pytest
from unittest.mock import MagicMock
from domain.accounts.services.auth_service import AuthService
from domain.accounts.aggregates.account import User
from domain.accounts.exceptions.auth_exceptions import InvalidCredentialsError, UserNotVerifiedError, UserNotFoundError

@pytest.fixture
def user_repository():
    return MagicMock()

@pytest.fixture
def auth_service(user_repository):
    return AuthService(user_repository)

@pytest.fixture
def user_data():
    return {
        'id': 1,
        'email': 'test@example.com',
        'name': 'Test User',
        'password': 'password123',
        'is_verified': True
    }

@pytest.fixture
def user(user_data):
    user_instance = User(**user_data)
    user_instance.check_password = MagicMock(return_value=True)
    return user_instance

def test_login_success(auth_service, user_repository, user, user_data):
    user_repository.get_by_email.return_value = user
    
    result = auth_service.login(user_data['email'], user_data['password'])
    
    assert result == user
    user_repository.get_by_email.assert_called_once_with(user_data['email'])
    user.check_password.assert_called_once_with(user_data['password'])

def test_login_user_not_found(auth_service, user_repository):
    user_repository.get_by_email.return_value = None
    
    with pytest.raises(UserNotFoundError):
        auth_service.login('nonexistent@example.com', 'password')

def test_login_invalid_credentials(auth_service, user_repository, user, user_data):
    user.check_password.return_value = False
    user_repository.get_by_email.return_value = user
    
    with pytest.raises(InvalidCredentialsError):
        auth_service.login(user_data['email'], 'wrongpassword')

def test_login_user_not_verified(auth_service, user_repository, user, user_data):
    user.is_verified = False
    user_repository.get_by_email.return_value = user
    
    with pytest.raises(UserNotVerifiedError):
        auth_service.login(user_data['email'], user_data['password'])
