# myapp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import api_translate, TranslationEndpointViewSet
from rest_framework.authtoken.views import obtain_auth_token

API_BASE_URL = 'api'

router = DefaultRouter()
router.register(rf'{API_BASE_URL}/endpoints', TranslationEndpointViewSet, basename='api_endpoints')

urlpatterns = [   
    # Translation Engine API
    path(f'{API_BASE_URL}/translate/<str:endpoint_id>', api_translate, name='api_translate'),

    # UI API
    path(f'{API_BASE_URL}/token', obtain_auth_token, name='api_token'),
    path('', include(router.urls)),
]