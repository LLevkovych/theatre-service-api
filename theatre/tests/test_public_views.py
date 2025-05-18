import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from theatre.models import Actor, Genre, Play

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_list_actors(api_client):
    Actor.objects.create(first_name="John", last_name="Doe")
    Actor.objects.create(first_name="Jane", last_name="Smith")
    url = reverse("theatre:actor-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 2
    first_names = [actor["first_name"] for actor in response.data["results"]]
    assert "John" in first_names
    assert "Jane" in first_names

@pytest.mark.django_db
def test_list_actors_empty(api_client):
    url = reverse("theatre:actor-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []

@pytest.mark.django_db
def test_list_genres(api_client):
    Genre.objects.create(name="Drama")
    Genre.objects.create(name="Comedy")
    url = reverse("theatre:genre-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 2
    genre_names = [genre["name"] for genre in response.data["results"]]
    assert "Drama" in genre_names
    assert "Comedy" in genre_names

@pytest.mark.django_db
def test_list_plays(api_client):
    genre = Genre.objects.create(name="Drama")
    play = Play.objects.create(title="Hamlet", description="Shakespeare play")
    play.genres.add(genre)
    url = reverse("theatre:play-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["title"] == "Hamlet"
    if "genres" in response.data["results"][0]:
        genres = response.data["results"][0]["genres"]
        genre_names = [g["name"] for g in genres]
        assert "Drama" in genre_names

@pytest.mark.django_db
def test_list_plays_empty(api_client):
    url = reverse("theatre:play-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []
