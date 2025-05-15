from rest_framework import serializers
from .models import Actor, Genre, Play, TheatreHall, Performance, Reservation, Ticket


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ["id", "first_name", "last_name"]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class PlaySerializer(serializers.ModelSerializer):
    actors = ActorSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Play
        fields = ["id", "title", "description", "actors", "genres"]


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = ["id", "name", "rows", "seats_in_row"]


class PerformanceSerializer(serializers.ModelSerializer):
    play = PlaySerializer(read_only=True)
    theatre_hall = TheatreHallSerializer(read_only=True)

    class Meta:
        model = Performance
        fields = ["id", "play", "theatre_hall", "show_time"]


class ReservationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    tickets = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Reservation
        fields = ["id", "user", "created_at", "tickets"]


class TicketSerializer(serializers.ModelSerializer):
    performance = PerformanceSerializer(read_only=True)
    reservation = ReservationSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "performance", "row", "seat", "reservation"]
