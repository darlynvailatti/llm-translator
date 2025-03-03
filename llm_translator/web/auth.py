from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import AccountAPIKey, Account

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

class CustomTokenAuthentication(BaseAuthentication):
    
    def authenticate(self, request):
        bearer_token = request.META.get('HTTP_AUTHORIZATION')
        if not bearer_token:
            return None

        try:
            token = bearer_token.split(' ')[1]
            active_api_key = AccountAPIKey.objects.filter(key=token, is_active=True).first()

            if not active_api_key:
                raise AuthenticationFailed('Invalid token or token is inactive')
            
            user = active_api_key.account.user
        except Exception as e:
            raise AuthenticationFailed(f'Error during authentication: {e}')
        
        return (user, None)
