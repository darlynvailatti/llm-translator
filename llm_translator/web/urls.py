# myapp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    api_translate,
    api_generate_spec_artifact,
    get_account_by_endpoint,
    api_run_spec_test_cases,
    TranslationEndpointViewSet,
    TranslationSpecViewSet,
    SpecTestCaseViewSet,
    SpecArtifactViewSet
)
from rest_framework.authtoken.views import obtain_auth_token

API_BASE_URL = "api"

router = DefaultRouter()
router.register(
    rf"{API_BASE_URL}/endpoints", TranslationEndpointViewSet, basename="api_endpoints"
)
router.register(
    rf"{API_BASE_URL}/endpoints/(?P<endpoint_id>[^/.]+)/specs",
    TranslationSpecViewSet,
    basename="api_specs",
)

router.register(
    rf"{API_BASE_URL}/specs/(?P<spec_id>[^/.]+)/testcases",
    SpecTestCaseViewSet,
    basename="api_testcases",
)

router.register(
    rf"{API_BASE_URL}/specs/(?P<spec_id>[^/.]+)/artifacts",
    SpecArtifactViewSet,
    basename="api_artifacts",
)

urlpatterns = [
    # Translation Engine API
    path(
        f"{API_BASE_URL}/translate/<str:endpoint_id>",
        api_translate,
        name="api_translate",
    ),
    path(
        f"{API_BASE_URL}/accounts/by_endpoint/<str:endpoint_id>",
        get_account_by_endpoint,
        name="api_account",
    ),
    path(
        f"{API_BASE_URL}/specs/<str:spec_id>/generate_artifact",
        api_generate_spec_artifact,
        name="api_generate_artifact",
    ),
    
    path(
        f"{API_BASE_URL}/specs/<str:spec_id>/testcases/run",
        api_run_spec_test_cases,
        name="api_run_testcases",
    ),

    # UI API
    path(f"{API_BASE_URL}/token", obtain_auth_token, name="api_token"),
    path("", include(router.urls)),
]
