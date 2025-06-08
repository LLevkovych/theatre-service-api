import datetime
import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from theatre.models import Reservation, Ticket, Performance, TheatreHall, Play
from user.models import User


@pytest.fixture
def theatre_hall(db):
    return TheatreHall.objects.create(
        name="Main Hall",
        rows=10,
        seats_in_row=15
    )


@pytest.fixture
def play(db):
    return Play.objects.create(title="Hamlet", description="Tragedy")


@pytest.fixture
def performance(db, play, theatre_hall):
    show_time = timezone.now() + datetime.timedelta(days=1)
    return Performance.objects.create(
        play=play,
        theatre_hall=theatre_hall,
        show_time=show_time
    )


@pytest.fixture
def user(db):
    return User.objects.create_user(username="user1", password="User123!")


@pytest.fixture
def user_client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client, user


@pytest.mark.django_db
def test_user_can_create_reservation_with_tickets(performance, user_client):
    client, user = user_client

    data = {
        "tickets": [
            {"performance_id": performance.id, "row": 1, "seat": 1},
            {"performance_id": performance.id, "row": 1, "seat": 2},
        ]
    }

    url = reverse("theatre:reservation-list")
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.data

    reservation_id = response.data["id"]
    reservation = Reservation.objects.get(id=reservation_id)
    tickets = Ticket.objects.filter(reservation=reservation)

    assert tickets.count() == 2
    assert tickets.filter(row=1, seat=1).exists()
    assert tickets.filter(row=1, seat=2).exists()
    assert reservation.user == user


@pytest.mark.django_db
def test_cannot_double_book_same_seat(performance, user_client):
    client, user = user_client

    reservation = Reservation.objects.create(user=user)
    Ticket.objects.create(
        row=1,
        seat=1,
        performance=performance,
        reservation=reservation
    )

    url = reverse("theatre:reservation-list")
    data = {
        "tickets": [
            {"performance_id": performance.id, "row": 1, "seat": 1},
        ]
    }
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert ("already" in str(response.data).lower()
            or "unique" in str(response.data).lower()
            )


@pytest.mark.django_db
def test_cannot_book_ticket_outside_hall_range(theatre_hall, user_client):
    client, user = user_client
    theatre_hall.rows = 5
    theatre_hall.seats_in_row = 10
    theatre_hall.save()

    play = Play.objects.create(
        title="Test Play",
        description="Test Description"
    )

    performance = Performance.objects.create(
        play=play,
        theatre_hall=theatre_hall,
        show_time=timezone.now() + datetime.timedelta(days=1),
    )

    url = reverse("theatre:reservation-list")

    data = {
        "tickets": [
            {"performance_id": performance.id, "row": 6, "seat": 1},
        ]
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert any(
        "Row number 6 is out of range for hall" in str(error)
        for error in response.data.get("tickets", [])
    )

    data = {
        "tickets": [
            {"performance_id": performance.id, "row": 1, "seat": 11},
        ]
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert any(
        "Seat number 11 is out of range in row 1" in str(error)
        for error in response.data.get("tickets", [])
    )


@pytest.mark.django_db
def test_user_cannot_create_reservation_without_tickets(user_client):
    client, _ = user_client
    url = reverse("theatre:reservation-list")
    response = client.post(url, {"tickets": []}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_user_cannot_update_reservation(user_client, performance):
    client, user = user_client
    data = {
        "tickets": [
            {"performance_id": performance.id, "row": 1, "seat": 1},
        ]
    }
    url = reverse("theatre:reservation-list")
    response = client.post(url, data, format="json")
    reservation_id = response.data["id"]

    patch_url = reverse("theatre:reservation-detail", args=[reservation_id])
    patch_data = {}
    patch_resp = client.patch(patch_url, patch_data, format="json")
    assert patch_resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_user_can_delete_reservation(user_client, performance):
    client, user = user_client

    data = {
        "tickets": [
            {"performance_id": performance.id, "row": 1, "seat": 1},
        ]
    }
    url = reverse("theatre:reservation-list")
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.data
    reservation_id = response.data["id"]

    del_url = reverse("theatre:reservation-detail", args=[reservation_id])
    del_resp = client.delete(del_url)
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT
