from django.apps import AppConfig


class BookingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookings'
    verbose_name = 'Booking Management'

    def ready(self):
        """
        Import signals when the app is ready
        """
        try:
            import bookings.signals  # noqa: F401
        except ImportError:
            pass