import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from user.models import User

REGISTER_URL = reverse("user:register")
PROFILE_URL = reverse("user:profile")
CHANGE_PASSWORD_URL = reverse("user:change-password")
LOGIN_URL = reverse("token_obtain_pair")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    def make_user(**kwargs):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        data.update(kwargs)
        return User.objects.create_user(**data)
    return make_user


@pytest.fixture
def authenticated_client(db, create_user):
    def make_authenticated_client(**user_kwargs):
        user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "StrongPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        user_data.update(user_kwargs)
        user = create_user(**user_data)

        client = APIClient()
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        response = client.post(LOGIN_URL, login_data, format="json")
        assert response.status_code == status.HTTP_200_OK, f"Login failed: {response.data}"

        token = response.data["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        return client, user

    return make_authenticated_client


@pytest.mark.django_db
class TestRegisterValidation:
    def test_register_username_taken(self, api_client, create_user):
        create_user(username="existinguser")
        data = {
            "username": "existinguser",
            "email": "unique@example.com",
            "password": "StrongPass123!",
            "password2": "StrongPass123!"
        }
        response = api_client.post(REGISTER_URL, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.data

    def test_register_email_taken(self, api_client, create_user):
        create_user(email="existing@example.com")
        data = {
            "username": "newuser",
            "email": "existing@example.com",
            "password": "StrongPass123!",
            "password2": "StrongPass123!"
        }
        response = api_client.post(REGISTER_URL, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_register_weak_password(self, api_client):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "123",
            "password2": "123"
        }
        response = api_client.post(REGISTER_URL, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data


@pytest.mark.django_db
class TestProfileUpdateValidation:
    def test_update_profile_invalid_email(self, authenticated_client):
        client, user = authenticated_client()
        payload = {
            "email": "invalid-email-format"
        }
        response = client.patch(PROFILE_URL, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data


@pytest.mark.django_db
class TestChangePasswordExtra:
    def test_change_password_to_same(self, authenticated_client):
        client, user = authenticated_client()
        payload = {
            "old_password": "StrongPass123!",
            "new_password": "StrongPass123!"
        }
        response = client.put(CHANGE_PASSWORD_URL, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data


@pytest.mark.django_db
class TestAuthentication:
    def test_login_success(self, api_client, create_user):
        user = create_user(
            username="loginuser",
            password="LoginPass123!"
        )
        data = {
            "username": "loginuser",
            "password": "LoginPass123!"
        }
        response = api_client.post(LOGIN_URL, data)
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_wrong_password(self, api_client, create_user):
        create_user(username="loginuser", password="LoginPass123!")
        data = {
            "username": "loginuser",
            "password": "WrongPass!"
        }
        response = api_client.post(LOGIN_URL, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestAccessControl:
    def test_unauthenticated_cannot_get_profile(self, api_client):
        response = api_client.get(PROFILE_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_cannot_update_profile(self, api_client):
        payload = {
            "first_name": "Hacker"
        }
        response = api_client.patch(PROFILE_URL, payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
