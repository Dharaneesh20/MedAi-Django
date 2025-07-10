from django.apps import AppConfig


class MedaiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'medai'
    
    def ready(self):
        # Initialize database when app is ready
        from .db import init_db
        init_db()
