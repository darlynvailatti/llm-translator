from django.core.management.base import BaseCommand
from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

class Command(BaseCommand):
    help = 'Auto-register all models with Django admin'

    def handle(self, *args, **kwargs):
        for model in apps.get_models():
            try:
                admin.site.register(model)
                self.stdout.write(self.style.SUCCESS(f'Successfully registered model {model.__name__}'))
            except AlreadyRegistered:
                self.stdout.write(self.style.WARNING(f'Model {model.__name__} is already registered'))
