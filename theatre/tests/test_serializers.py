import pytest
from theatre.models import Actor, Genre, Play
from theatre.serializers import ActorSerializer, GenreSerializer, PlaySerializer


@pytest.mark.django_db
def test_actor_serializer():
    actor = Actor.objects.create(first_name="Tom", last_name="Hanks")
    data = ActorSerializer(actor).data
    assert data["first_name"] == "Tom"
    assert data["last_name"] == "Hanks"


@pytest.mark.django_db
def test_actor_serializer_validation_error():
    data = {"first_name": "", "last_name": ""}
    serializer = ActorSerializer(data=data)
    assert not serializer.is_valid()
    assert "first_name" in serializer.errors
    assert "last_name" in serializer.errors


@pytest.mark.django_db
def test_genre_serializer():
    genre = Genre.objects.create(name="Drama")
    data = GenreSerializer(genre).data
    assert data["name"] == "Drama"


@pytest.mark.django_db
def test_genre_serializer_validation_error():
    data = {"name": ""}
    serializer = GenreSerializer(data=data)
    assert not serializer.is_valid()
    assert "name" in serializer.errors


@pytest.mark.django_db
def test_play_serializer():
    genre = Genre.objects.create(name="Comedy")
    play = Play.objects.create(title="Funny Show", description="A very funny play")
    play.genres.add(genre)
    data = PlaySerializer(play).data
    assert data["title"] == "Funny Show"
    assert "Comedy" in [g["name"] for g in data.get("genres", [])]


@pytest.mark.django_db
def test_play_serializer_validation_error():
    data = {"title": "", "description": ""}
    serializer = PlaySerializer(data=data)
    assert not serializer.is_valid()
    assert "title" in serializer.errors
