from rest_framework import serializers
from theatre.models import (
    Actor,
    Genre,
    Play,
    TheatreHall,
    Performance,
    Reservation,
    Ticket
)

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

    actor_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Actor.objects.all(), source="actors", write_only=True, required=False
    )
    genre_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Genre.objects.all(), source="genres", write_only=True, required=False
    )

    class Meta:
        model = Play
        fields = ["id", "title", "description", "actors", "genres", "actor_ids", "genre_ids"]

    def create(self, validated_data):
        actors = validated_data.pop("actors", [])
        genres = validated_data.pop("genres", [])
        play = Play.objects.create(**validated_data)
        play.actors.set(actors)
        play.genres.set(genres)
        return play

    def update(self, instance, validated_data):
        actors = validated_data.pop("actors", None)
        genres = validated_data.pop("genres", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if actors is not None:
            instance.actors.set(actors)
        if genres is not None:
            instance.genres.set(genres)
        return instance


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = ["id", "name", "rows", "seats_in_row"]


class PerformanceSerializer(serializers.ModelSerializer):
    play = PlaySerializer(read_only=True)
    theatre_hall = TheatreHallSerializer(read_only=True)

    play_id = serializers.PrimaryKeyRelatedField(
        queryset=Play.objects.all(), source="play", write_only=True
    )
    theatre_hall_id = serializers.PrimaryKeyRelatedField(
        queryset=TheatreHall.objects.all(), source="theatre_hall", write_only=True
    )

    class Meta:
        model = Performance
        fields = ["id", "play", "theatre_hall", "show_time", "play_id", "theatre_hall_id"]


class TicketSerializer(serializers.ModelSerializer):
    performance = PerformanceSerializer(read_only=True)
    performance_id = serializers.PrimaryKeyRelatedField(
        queryset=Performance.objects.all(), source="performance", write_only=True
    )

    reservation = serializers.PrimaryKeyRelatedField(read_only=True)
    reservation_id = serializers.PrimaryKeyRelatedField(
        queryset=Reservation.objects.all(), source="reservation", write_only=True
    )

    class Meta:
        model = Ticket
        fields = ["id", "performance", "performance_id", "row", "seat", "reservation", "reservation_id"]


class TicketCreateSerializer(serializers.ModelSerializer):
    performance_id = serializers.PrimaryKeyRelatedField(
        queryset=Performance.objects.all(),
        source="performance",
    )

    class Meta:
        model = Ticket
        fields = ["performance_id", "row", "seat"]


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketCreateSerializer(many=True, write_only=True)
    tickets_info = TicketSerializer(many=True, read_only=True, source="tickets")

    class Meta:
        model = Reservation
        fields = ["id", "created_at", "tickets", "tickets_info"]

    def validate(self, attrs):
        tickets_data = attrs.get("tickets", [])
        if not tickets_data:
            raise serializers.ValidationError({"tickets": "At least one ticket must be provided."})

        performance_ids = set()
        checked_seats = set()

        for ticket in tickets_data:
            performance = ticket["performance"]
            row = ticket["row"]
            seat = ticket["seat"]

            theatre_hall = performance.theatre_hall

            if row < 1 or row > theatre_hall.rows:
                raise serializers.ValidationError(
                    {"tickets": f"Row number {row} is out of range for hall '{theatre_hall.name}'."}
                )

            if seat < 1 or seat > theatre_hall.seats_in_row:
                raise serializers.ValidationError(
                    {"tickets": f"Seat number {seat} is out of range in row {row}."}
                )

            if Ticket.objects.filter(performance=performance, row=row, seat=seat).exists():
                raise serializers.ValidationError(
                    {"tickets": f"Seat {row}-{seat} is already booked for performance {performance.id}."}
                )

            if (performance.id, row, seat) in checked_seats:
                raise serializers.ValidationError(
                    {"tickets": f"Duplicate seat {row}-{seat} in request for performance {performance.id}."}
                )
            checked_seats.add((performance.id, row, seat))

            performance_ids.add(performance.id)

        if len(performance_ids) > 1:
            raise serializers.ValidationError(
                {"tickets": "All tickets in one reservation must be for the same performance."}
            )

        return attrs

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        user = self.context["request"].user

        reservation = Reservation.objects.create(user=user)

        Ticket.objects.bulk_create([
            Ticket(reservation=reservation, **ticket_data)
            for ticket_data in tickets_data
        ])

        return reservation
