from rest_framework.decorators import api_view
from rest_framework.response import Response
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