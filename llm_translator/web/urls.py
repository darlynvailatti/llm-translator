# myapp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import api_translate, get_account_by_endpoint, TranslationEndpointViewSet, TranslationSpecViewSet
from rest_framework.authtoken.views import obtain_auth_token

API_BASE_URL = 'api'

router = DefaultRouter()
router.register(rf'{API_BASE_URL}/endpoints', TranslationEndpointViewSet, basename='api_endpoints')
router.register(rf'{API_BASE_URL}/endpoints/(?P<endpoint_id>[^/.]+)/specs', TranslationSpecViewSet, basename='api_specs')

urlpatterns = [   
    # Translation Engine API
    path(f'{API_BASE_URL}/translate/<str:endpoint_id>', api_translate, name='api_translate'),
    path(f'{API_BASE_URL}/accounts/by_endpoint/<str:endpoint_id>', get_account_by_endpoint, name='api_account'),

    # UI API
    path(f'{API_BASE_URL}/token', obtain_auth_token, name='api_token'),
    path('', include(router.urls)),
]