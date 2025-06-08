from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from theatre.models import (
    Actor, Genre, Play, TheatreHall,
    Performance, Reservation, Ticket
)
from theatre.permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from theatre.serializers import (
    ActorSerializer,
    GenreSerializer,
    PlaySerializer,
    TheatreHallSerializer,
    PerformanceSerializer,
    ReservationSerializer,
    TicketSerializer
)
from theatre.schemas import (
    actor_schema,
    genre_schema,
    play_schema,
    theatre_hall_schema,
    performance_schema,
    reservation_schema,
    ticket_schema,
)


@actor_schema
class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["first_name", "last_name"]
    ordering_fields = ["first_name", "last_name"]
    search_fields = ["first_name", "last_name"]


@genre_schema
class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["name"]
    search_fields = ["name"]


@play_schema
class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["genres__name"]
    ordering_fields = ["title"]
    search_fields = ["title", "description"]


@theatre_hall_schema
class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return super().get_permissions()


@performance_schema
class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["play__title", "show_time"]
    ordering_fields = ["show_time", "play__title"]
    search_fields = ["play__title"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return super().get_permissions()


@reservation_schema
class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Updating reservations is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Partial updating reservations is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


@ticket_schema
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related("reservation", "performance")
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(reservation__user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
