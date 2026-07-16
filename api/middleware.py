import django.core.signing as signing
from django.contrib.auth.models import User

class GraphQLAuthMiddleware:
    """
    Middleware to authenticate users based on a signed token in 
    either the 'Authorization' header or the 'detache_session' cookie.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            token = request.COOKIES.get('detache_session')

        if token:
            try:
                # Validate the token using Django's secure signing system.
                # Max age is set to 24 hours (86400 seconds).
                data = signing.loads(token, max_age=86400)
                user_id = data.get('user_id')
                if user_id:
                    user = User.objects.get(pk=user_id)
                    request.user = user
            except Exception:
                # Token expired, invalid signature, or user does not exist
                pass

        return self.get_response(request)
