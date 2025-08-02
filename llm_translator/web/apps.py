from django.apps import AppConfig

class WebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web'

    def ready(self):
        from .llm.llm_providers import configure_dspy_lm
        configure_dspy_lm()
        import web.signals
