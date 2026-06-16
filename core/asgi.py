"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
import channels_graphql_ws
from core.schema import schema

class MyGraphQLSubscriptionConsumer(channels_graphql_ws.GraphqlWsConsumer):
    schema = schema

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/graphql", MyGraphQLSubscriptionConsumer.as_asgi()),
            path("ws/graphql/", MyGraphQLSubscriptionConsumer.as_asgi()),
        ])
    ),
})

