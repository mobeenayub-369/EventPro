from django.apps import AppConfig


class EventsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'events'
    verbose_name = 'Event Services'

    def ready(self):
        """
        Import signals when the app is ready
        This method is called when Django starts
        """
        try:
            import events.signals  # noqa: F401
        except ImportError:
            pass