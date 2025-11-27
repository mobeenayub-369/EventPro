from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    """
    App configuration for the categories application.
    Provides metadata and configuration for Django.
    """

    # Default primary key field type for models
    default_auto_field = 'django.db.models.BigAutoField'

    # Name of the application (Python path)
    name = 'categories'

    # Human-readable name for the application
    verbose_name = 'Event Categories'