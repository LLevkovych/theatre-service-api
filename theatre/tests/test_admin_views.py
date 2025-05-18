import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from user.models import User


@pytest.fixture
def admin_client(db):
    admin = User.objects.create_superuser(
        username="admin",
        password="Admin123!"
    )
    client = APIClient()
    client.force_authenticate(admin)
    return client


@pytest.mark.django_db
@pytest.mark.parametrize(
    "model_name, create_data, update_data, url_name",
    [
        (
            "actor",
            {"first_name": "Tom", "last_name": "Cruise"},
            {"first_name": "New", "last_name": "Name"},
            "theatre:actor",
        ),
        ("genre", {"name": "Drama"}, {"name": "Comedy"}, "theatre:genre"),
        (
            "play",
            {
                "title": "Hamlet",
                "description": "Tragedy",
                "actor_ids": [],
                "genre_ids": [],
            },
            {
                "title": "Macbeth",
                "description": "Tragedy",
                "actor_ids": [],
                "genre_ids": [],
            },
            "theatre:play",
        ),
        (
            "theatrehall",
            {"name": "Main Hall", "rows": 10, "seats_in_row": 15},
            {"name": "Secondary Hall", "rows": 5, "seats_in_row": 10},
            "theatre:theatrehall",
        ),
    ],
)
def test_admin_crud_basic(
        admin_client,
        model_name,
        create_data,
        update_data,
        url_name
):
    client = admin_client

    url_list = reverse(f"{url_name}-list")
    response = client.post(url_list, create_data, format="json")
    assert (
        response.status_code == status.HTTP_201_CREATED
    ), f"Failed creating {model_name}: {response.data}"
    obj_id = response.data["id"]

    url_detail = reverse(f"{url_name}-detail", args=[obj_id])
    response = client.get(url_detail)
    assert response.status_code == status.HTTP_200_OK

    response = client.put(url_detail, update_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    for key, value in update_data.items():
        if key in response.data:
            assert response.data[key] == value

    patch_key = list(update_data.keys())[0]
    patch_val = update_data[patch_key]
    patch_data = {
        patch_key: patch_val + " PATCH"
        if isinstance(patch_val, str) else patch_val
    }
    response = client.patch(url_detail, patch_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data[patch_key] == patch_data[patch_key]

    response = client.delete(url_detail)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_admin_performance_id_if_crud(admin_client):
    client = admin_client
    genre = client.post(
        reverse("theatre:genre-list"), {"name": "Drama"}, format="json"
    ).data
    actor = client.post(
        reverse("theatre:actor-list"),
        {"first_name": "Tom", "last_name": "Hanks"},
        format="json",
    ).data
    play_data = {
        "title": "Hamlet",
        "description": "Tragedy",
        "actor_ids": [actor["id"]],
        "genre_ids": [genre["id"]],
    }
    play_resp = client.post(
        reverse("theatre:play-list"),
        play_data, format="json"
    )
    assert play_resp.status_code == status.HTTP_201_CREATED
    play_id = play_resp.data["id"]

    theatre_hall_resp = client.post(
        reverse("theatre:theatrehall-list"),
        {"name": "Main Hall", "rows": 10, "seats_in_row": 15},
        format="json",
    )
    assert theatre_hall_resp.status_code == status.HTTP_201_CREATED
    theatre_hall_id = theatre_hall_resp.data["id"]

    performance_data = {
        "play_id": play_id,
        "theatre_hall_id": theatre_hall_id,
        "show_time": "2030-01-01T20:00:00Z",
    }
    url_list = reverse("theatre:performance-list")
    resp = client.post(url_list, performance_data, format="json")
    assert resp.status_code == status.HTTP_201_CREATED
    performance_id = resp.data["id"]

    url_detail = reverse("theatre:performance-detail", args=[performance_id])
    update_data = {
        "play_id": play_id,
        "theatre_hall_id": theatre_hall_id,
        "show_time": "2030-01-02T20:00:00Z",
    }
    resp = client.put(url_detail, update_data, format="json")
    assert resp.status_code == status.HTTP_200_OK

    patch_data = {"show_time": "2030-01-03T20:00:00Z"}
    resp = client.patch(url_detail, patch_data, format="json")
    assert resp.status_code == status.HTTP_200_OK

    resp = client.delete(url_detail)
    assert resp.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_admin_reservation_and_ticket_crud(admin_client):
    client = admin_client

    genre = client.post(
        reverse("theatre:genre-list"), {"name": "Drama"}, format="json"
    ).data
    actor = client.post(
        reverse("theatre:actor-list"),
        {"first_name": "Tom", "last_name": "Hanks"},
        format="json",
    ).data
    play = client.post(
        reverse("theatre:play-list"),
        {
            "title": "Hamlet",
            "description": "Tragedy",
            "actor_ids": [actor["id"]],
            "genre_ids": [genre["id"]],
        },
        format="json",
    ).data

    theatre_hall = client.post(
        reverse("theatre:theatrehall-list"),
        {"name": "Main Hall", "rows": 10, "seats_in_row": 15},
        format="json",
    ).data

    performance = client.post(
        reverse("theatre:performance-list"),
        {
            "play_id": play["id"],
            "theatre_hall_id": theatre_hall["id"],
            "show_time": "2030-01-01T20:00:00Z",
        },
        format="json",
    ).data

    reservation_resp = client.post(
        reverse("theatre:reservation-list"),
        {"tickets": [
                 {"performance_id": performance["id"],
                  "row": 1, "seat": 1}
             ]},
        format="json",
    )
    assert reservation_resp.status_code == status.HTTP_201_CREATED
    reservation = reservation_resp.data
    reservation_id = reservation["id"]
    ticket = reservation["tickets_info"][0]
    ticket_id = ticket["id"]

    reservation_detail_url = reverse(
        "theatre:reservation-detail", args=[reservation_id]
    )
    resp = client.get(reservation_detail_url)
    assert resp.status_code == status.HTTP_200_OK

    ticket_detail_url = reverse("theatre:ticket-detail", args=[ticket_id])
    patch_resp = client.patch(ticket_detail_url, {"row": 2}, format="json")
    assert patch_resp.status_code == status.HTTP_200_OK
    assert patch_resp.data["row"] == 2

    delete_resp = client.delete(ticket_detail_url)
    assert delete_resp.status_code == status.HTTP_204_NO_CONTENT

    delete_resp = client.delete(reservation_detail_url)
    assert delete_resp.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url_name, invalid_data",
    [
        ("theatre:actor-list", {"first_name": "", "last_name": ""}),
        ("theatre:genre-list", {"name": ""}),
        (
            "theatre:play-list",
            {"title": "", "description": "", "actor_ids": [], "genre_ids": []},
        ),
        ("theatre:theatrehall-list",
         {"name": "",
          "rows": -1,
          "seats_in_row": -1
          }
         ),
    ],
)
def test_admin_invalid_data(admin_client, url_name, invalid_data):
    client = admin_client
    url = reverse(url_name)
    resp = client.post(url, invalid_data, format="json")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
