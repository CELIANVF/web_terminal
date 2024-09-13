# web_terminal/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import ssh.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_terminal.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ssh.routing.websocket_urlpatterns
        )
    ),
})
