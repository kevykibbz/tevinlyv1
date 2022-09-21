import os
import django
from channels.routing import ProtocolTypeRouter,URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings')
django.setup()
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from notifications.routing import websocket_urlpatterns
from channels.security.websocket import AllowedHostsOriginValidator

application = ProtocolTypeRouter({
    "http":get_asgi_application(),
    "websocket":AllowedHostsOriginValidator(
          AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    )
})