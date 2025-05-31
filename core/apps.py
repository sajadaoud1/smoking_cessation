from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

class NotificationsConfig(AppConfig):
    name = 'notifications'

    def ready(self):
        import utils.tasks