# myapp/urls.py
from django.urls import path
from .views import api_translate

urlpatterns = [
    path('api/translate/<str:endpoint_id>', api_translate, name='api_translate'),
]