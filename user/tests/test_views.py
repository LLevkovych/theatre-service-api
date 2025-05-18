import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from user.models import User

REGISTER_URL = reverse("user:register")
PROFILE_URL = reverse("user:profile")
CHANGE_PASSWORD_URL = reverse("user:change-password")
LOGOUT_URL = reverse("user:logout")


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
def authenticated_client(api_client, create_user):
    user = create_user()
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.mark.django_db
class TestRegisterView:
    def test_register_success(self, api_client):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "StrongPass123!",
            "password2": "StrongPass123!"
        }
        response = api_client.post(REGISTER_URL, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username="newuser").exists()

    def test_register_passwords_do_not_match(self, api_client):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "12345678",
            "password2": "87654321"
        }
        response = api_client.post(REGISTER_URL, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data


@pytest.mark.django_db
class TestProfileView:
    def test_retrieve_profile_authenticated(self, authenticated_client):
        client, user = authenticated_client
        response = client.get(PROFILE_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == user.username

    def test_retrieve_profile_unauthenticated(self, api_client):
        response = api_client.get(PROFILE_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self, authenticated_client):
        client, user = authenticated_client
        payload = {
            "first_name": "Updated",
            "last_name": "Name"
        }
        response = client.patch(PROFILE_URL, payload)
        user.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert user.first_name == "Updated"
        assert user.last_name == "Name"


@pytest.mark.django_db
class TestChangePasswordView:
    def test_change_password_successfully(self, authenticated_client):
        client, user = authenticated_client
        payload = {
            "old_password": "StrongPass123!",
            "new_password": "NewStrongPass456!"
        }
        response = client.put(CHANGE_PASSWORD_URL, payload)
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password("NewStrongPass456!")

    def test_change_password_wrong_old_password(self, authenticated_client):
        client, _ = authenticated_client
        payload = {
            "old_password": "WrongOldPass",
            "new_password": "NewStrongPass456!"
        }
        response = client.put(CHANGE_PASSWORD_URL, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "old_password" in response.data

    def test_change_password_unauthenticated(self, api_client):
        payload = {
            "old_password": "StrongPass123!",
            "new_password": "NewStrongPass456!"
        }
        response = api_client.put(CHANGE_PASSWORD_URL, payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestLogoutView:
    def test_logout_success(self, authenticated_client):
        client, user = authenticated_client
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        response = client.post(LOGOUT_URL, {"refresh": str(refresh)})
        assert response.status_code == status.HTTP_205_RESET_CONTENT

    def test_logout_no_token(self, authenticated_client):
        client, _ = authenticated_client
        response = client.post(LOGOUT_URL, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_invalid_token(self, authenticated_client):
        client, _ = authenticated_client
        response = client.post(LOGOUT_URL, {"refresh": "invalidtoken"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
