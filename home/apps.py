from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"
    # Duct tape
    verbose_name = "⠀Add Info"

    def ready(self):
        # Initialization of signals
        import home.signals
        return super().ready()
