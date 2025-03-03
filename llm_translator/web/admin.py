from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from .models import TranslationEndpoint, TranslationSpec

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
