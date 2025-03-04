from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from .models import TranslationEndpoint, TranslationSpec, TranslationEvent
from django.core.management import call_command

class JSONAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

@admin.register(TranslationEndpoint)
class TranslationEndpointAdmin(JSONAdmin):
    pass

@admin.register(TranslationSpec)
class TranslationSpecAdmin(JSONAdmin):
    pass

@admin.register(TranslationEvent)
class TranslationEventAdmin(JSONAdmin):
    pass


call_command('register_all_models')