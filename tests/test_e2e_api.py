import pytest
import requests

BASE_URL = "http://localhost:8000/api/v1"


@pytest.fixture(scope="module")
def registered_user_data():
    email = "test_e2e@example.com"
    password = "securepassword123"
    name = "Test E2E User"
    return {"email": email, "password": password, "name": name}


@pytest.fixture(scope="module")
def authenticated_client(registered_user_data):
    # Register a user
    register_url = f"{BASE_URL}/accounts/register/"
    response = requests.post(
        register_url,
        json={
            "email": registered_user_data["email"],
            "password": registered_user_data["password"],
            "password2": registered_user_data["password"],
            "name": registered_user_data["name"],
        },
    )
    if response.status_code == 409:
        # User already exists, proceed to obtain token
        pass
    else:
        assert response.status_code == 201

    # Verify email (assuming a mock or direct call for simplicity in E2E setup)
    # In a real E2E, you'd likely need to capture the token from an email or mock the email service.
    # For this test, we'll assume verification happens or is not strictly required for token obtain.
    # If verification is required, this fixture would need to be more complex.

    # Obtain token
    token_url = "http://localhost:8000/api/token/"
    response = requests.post(
        token_url, json={"email": registered_user_data["email"], "password": registered_user_data["password"]}
    )
    assert response.status_code == 200
    tokens = response.json()
    access_token = tokens["access"]
    refresh_token = tokens["refresh"]

    class AuthenticatedClient:
        def __init__(self, access_token, refresh_token):
            self.access_token = access_token
            self.refresh_token = refresh_token
            self.headers = {"Authorization": f"Bearer {self.access_token}"}
            print(f"AuthenticatedClient initialized with access_token: {self.access_token}")
            print(f"AuthenticatedClient headers: {self.headers}")

        def get(self, path):
            print(f"GET request to {BASE_URL}{path} with headers: {self.headers}")
            return requests.get(f"{BASE_URL}{path}", headers=self.headers)

        def post(self, path, json=None):
            print(f"POST request to {BASE_URL}{path} with json: {json} and headers: {self.headers}")
            return requests.post(f"{BASE_URL}{path}", json=json, headers=self.headers)

        def patch(self, path, json=None):
            print(f"PATCH request to {BASE_URL}{path} with json: {json} and headers: {self.headers}")
            return requests.patch(f"{BASE_URL}{path}", json=json, headers=self.headers)

    return AuthenticatedClient(access_token, refresh_token)


def test_user_registration(registered_user_data):
    url = f"{BASE_URL}/accounts/register/"
    import time

    unique_email = f"new_e2e_user_{int(time.time())}@example.com"
    response = requests.post(
        url,
        json={
            "email": unique_email,
            "password": "newsecurepassword123",
            "password2": "newsecurepassword123",
            "name": "New E2E User",
        },
    )
    assert response.status_code == 201
    assert f"Usuário {unique_email} criado com sucesso." in response.json()["message"]

    # Test registration with existing email
    response = requests.post(
        url,
        json={
            "email": unique_email,
            "password": "newsecurepassword123",
            "password2": "newsecurepassword123",
            "name": "New E2E User",
        },
    )
    assert response.status_code == 409
    assert "já existe." in response.json()["email"]


def test_token_obtain(registered_user_data):
    url = "http://localhost:8000/api/token/"
    response = requests.post(
        url, json={"email": registered_user_data["email"], "password": registered_user_data["password"]}
    )
    assert response.status_code == 200
    assert "access" in response.json()
    assert "refresh" in response.json()


def test_token_refresh(authenticated_client):
    url = "http://localhost:8000/api/token/refresh/"
    response = requests.post(url, json={"refresh": authenticated_client.refresh_token})
    assert response.status_code == 200
    assert "access" in response.json()


def test_user_me_get(authenticated_client):
    url = "/users/me"
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert "email" in response.json()
    assert "name" in response.json()
    assert "bio" in response.json()


def test_user_me_patch(authenticated_client):
    url = "/users/me"
    new_name = "Updated E2E Name"
    new_bio = "This is an updated bio for E2E testing."
    response = authenticated_client.patch(url, {"name": new_name, "bio": new_bio})
    assert response.status_code == 200
    assert response.json()["name"] == new_name
    assert response.json()["bio"] == new_bio

    # Verify the changes by getting the user info again
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert response.json()["name"] == new_name
    assert response.json()["bio"] == new_bio


def test_change_password(authenticated_client, registered_user_data):
    url = "/accounts/change-password/"
    old_password = registered_user_data["password"]
    new_password = "new_secure_password_456"

    response = authenticated_client.post(
        url, json={"old_password": old_password, "new_password": new_password, "confirm_new_password": new_password}
    )
    assert response.status_code == 200
    assert "Senha alterada com sucesso." in response.json()["message"]

    # Try to log in with the old password (should fail)
    token_url = "http://localhost:8000/api/token/"
    response = requests.post(token_url, json={"email": registered_user_data["email"], "password": old_password})
    assert response.status_code == 401

    # Try to log in with the new password (should succeed)
    response = requests.post(token_url, json={"email": registered_user_data["email"], "password": new_password})
    assert response.status_code == 200
    assert "access" in response.json()
    assert "refresh" in response.json()


# Note: Email verification and resend email tests are more complex for E2E
# as they typically involve an email service. For a true E2E, you'd need
# to mock the email service or have a way to capture the verification token.
# For now, these are omitted to keep the E2E test focused on direct API interactions.
# If a mock email service or a way to retrieve the token is available,
# these tests can be added.
