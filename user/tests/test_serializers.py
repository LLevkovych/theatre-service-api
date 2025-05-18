import pytest
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import ValidationError as DRFValidationError
from user.models import User
from user.serializers import ChangePasswordSerializer


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        username="testuser",
        password="OldPass123!"
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "old_password, new_password, expected_valid, expected_error_field",
    [
        ("OldPass123!", "NewStrongPass456!", True, None),
        ("WrongPass!", "NewStrongPass456!", False, "old_password"),
        ("OldPass123!", "123", False, "new_password"),
    ],
)
def test_change_password_serializer(
    test_user, old_password, new_password, expected_valid, expected_error_field
):
    factory = APIRequestFactory()
    request = factory.put("/")
    request.user = test_user

    data = {
        "old_password": old_password,
        "new_password": new_password,
    }

    serializer = ChangePasswordSerializer(
        data=data,
        context={"request": request}
    )

    if expected_valid:
        assert serializer.is_valid(), serializer.errors
        serializer.save()
        test_user.refresh_from_db()
        assert test_user.check_password(new_password)
    else:
        with pytest.raises(DRFValidationError):
            serializer.is_valid(raise_exception=True)
