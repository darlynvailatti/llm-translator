from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from .models import (
    TranslationEndpoint,
    Account,
    TranslationSpec,
    SpecTestCase,
    TranslationArtifact,
)
from .serializers import (
    TranslationEndpointListSerializer,
    TranslationEndpointDetailSerializer,
    TranslationSpecListSerializer,
    TranslationSpecDetailSerializer,
    AccountSerializer,
    SpecTestCaseDetailSerializer,
    SpecTestCaseListSerializer,
    TranslationSpecArtifactSerializer,
)
from .manager import (
    TranslationManager,
    TranslationRequest,
    ArtifactGeneratorManager,
    ArtifactGenerationRequest
)


@api_view(["POST"])
def api_translate(request, endpoint_id):
    content_type = request.headers.get("Content-Type")
    body = request.body

    translation_request = {
        "endpoint_id": endpoint_id,
        "content_type": content_type,
        "body": body,
    }

    t_request = TranslationRequest(**translation_request)
    t_response = TranslationManager().handle(t_request)

    status = 200 if t_response.success else 400

    return Response(
        {
            "success": t_response.success,
            "message": t_response.message,
            "duration": t_response.duration,
            "content_type": t_response.content_type,
            "body": t_response.body,
        },
        status=status,
    )


@api_view(["GET"])
def get_account_by_endpoint(request, endpoint_id):
    account = TranslationEndpoint.objects.filter(uuid=endpoint_id).first()
    if not account:
        return Response(
            {"error": "No active Account has been found for the given endpoint"},
            status=400,
        )
    data = AccountSerializer(account.owner).data
    return Response(data, status=200)


@api_view(["POST"])
def api_generate_spec_artifact(request, spec_id):
    try:
        request = ArtifactGenerationRequest(spec_id=spec_id)
        response = ArtifactGeneratorManager().handle(request)

        if not response.success:
            return Response({"success": False, "error": response.message}, status=400)
        elif not response.artifact:
            return Response(
                {"success": False, "error": "No artifact has been generated"},
                status=400,
            )
        else:
            return Response(
                {
                    "success": True,
                    "artifact": TranslationSpecArtifactSerializer(
                        response.artifact
                    ).data,
                },
                status=201,
            )
    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=400)


class TranslationEndpointViewSet(viewsets.ModelViewSet):

    authentication_classes = [
        TokenAuthentication,
    ]

    serializer_class = TranslationEndpointListSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TranslationEndpointListSerializer
        return TranslationEndpointDetailSerializer

    def get_queryset(self):
        account = self.__get_account_for_user(self.request)
        return TranslationEndpoint.objects.filter(owner=account)

    def create(self, request, *args, **kwargs):
        TranslationEndpointDetailSerializer(data=request.data).is_valid(
            raise_exception=True
        )
        account = self.__get_account_for_user(request)

        endpoint = TranslationEndpoint.objects.create(owner=account, **request.data)
        created = TranslationEndpointDetailSerializer(endpoint).data
        return Response(created, status=201)

    def __get_account_for_user(self, request):
        account = Account.objects.filter(user=request.user, is_active=True).first()
        if not account:
            return Response(
                {"error": "No active Account has been found for your user"}, status=400
            )
        return account


class TranslationSpecViewSet(viewsets.ModelViewSet):

    authentication_classes = [
        TokenAuthentication,
    ]

    def get_queryset(self):
        endpoint_id = self.kwargs["endpoint_id"]
        return TranslationSpec.objects.filter(endpoint_id=endpoint_id)

    def get_serializer_class(self):
        if self.action == "list":
            return TranslationSpecListSerializer
        return TranslationSpecDetailSerializer

    def create(self, request, *args, **kwargs):
        TranslationSpecDetailSerializer(data=request.data).is_valid(
            raise_exception=True
        )
        endpoint = get_object_or_404(
            TranslationEndpoint, uuid=self.kwargs["endpoint_id"]
        )

        created = TranslationSpec.objects.create(endpoint=endpoint, **request.data)
        return Response(TranslationSpecDetailSerializer(created).data, status=201)


class SpecTestCaseViewSet(viewsets.ModelViewSet):

    authentication_classes = [
        TokenAuthentication,
    ]

    def get_queryset(self):
        spec_id = self.kwargs["spec_id"]
        return SpecTestCase.objects.filter(spec_id=spec_id)

    def get_serializer_class(self):
        if self.action == "list":
            return SpecTestCaseListSerializer
        return SpecTestCaseDetailSerializer

    def create(self, request, *args, **kwargs):
        SpecTestCaseDetailSerializer(data=request.data).is_valid(raise_exception=True)
        spec = get_object_or_404(TranslationSpec, uuid=self.kwargs["spec_id"])

        created = SpecTestCase.objects.create(spec=spec, **request.data)
        return Response(SpecTestCaseDetailSerializer(created).data, status=201)


class SpecArtifactViewSet(viewsets.ModelViewSet):

    authentication_classes = [
        TokenAuthentication,
    ]

    def get_queryset(self):
        spec_id = self.kwargs["spec_id"]
        return TranslationArtifact.objects.filter(spec_id=spec_id)

    def get_serializer_class(self):
        return TranslationSpecArtifactSerializer

    def create(self, request, *args, **kwargs):
        raise NotImplementedError("Create not supported for this endpoint")
