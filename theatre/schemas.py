from drf_spectacular.utils import extend_schema

actor_schema = extend_schema(
    summary="Actor API",
    description="API для створення, перегляду, редагування та видалення акторів (тільки для адмінів)."
)

genre_schema = extend_schema(
    summary="Genre API",
    description="API для роботи з жанрами. Читання доступне всім, зміни — тільки для авторизованих."
)

play_schema = extend_schema(
    summary="Play API",
    description="API для керування пʼєсами. Пошук за назвою, описом та жанрами."
)

theatre_hall_schema = extend_schema(
    summary="Theatre Hall API",
    description="API для залів театру. Зміни дозволені лише для адмінів."
)

performance_schema = extend_schema(
    summary="Performance API",
    description="API для вистав. Пошук за назвою пʼєси та датою. Зміни лише для адмінів."
)

reservation_schema = extend_schema(
    summary="Reservation API",
    description="API для перегляду та створення бронювань. Кожен бачить тільки свої."
)

ticket_schema = extend_schema(
    summary="Ticket API",
    description="API для квитків користувача. Адміни бачать усі, користувач — лише свої."
)
