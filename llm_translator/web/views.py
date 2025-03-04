from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from .models import TranslationEndpoint, Account
from .serializers import TranslationEndpointListSerializer, TranslationEndpointDetailSerializer
from .manager import TranslationManager, TranslationRequest

@api_view(['POST'])
def api_translate(request, endpoint_id):
    content_type = request.headers.get('Content-Type')
    body = request.data

    translation_request = {
        "endpoint_id": endpoint_id,
        "content_type": content_type,
        "body": body,
    }

    t_request = TranslationRequest(**translation_request)
    t_response = TranslationManager().handle(t_request)
   
    status = 200 if t_response.success else 400
    
    return Response({
        "success": t_response.success,
        "message": t_response.message,
        "duration": t_response.duration,
        "content_type": t_response.content_type,
        "body": t_response.body
    }, status=status)

class TranslationEndpointViewSet(viewsets.ModelViewSet):

    authentication_classes = [
        TokenAuthentication,
    ]

    serializer_class = TranslationEndpointListSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return TranslationEndpointListSerializer
        return TranslationEndpointDetailSerializer

    def get_queryset(self):
        account = self.__get_account_for_user(self.request)
        return TranslationEndpoint.objects.filter(owner=account)
    
    def create(self, request, *args, **kwargs):
        TranslationEndpointDetailSerializer(data=request.data).is_valid(raise_exception=True)
        account = self.__get_account_for_user(request)

        TranslationEndpoint.objects.create(
            owner=account,
            **request.data
        )
        return Response({"success": "Endpoint created"}, status=201)
    
    def __get_account_for_user(self, request):
        account = Account.objects.filter(user=request.user, is_active=True).first()
        if not account:
            return Response({"error": "No active Account has been found for your user"}, status=400)
        return account