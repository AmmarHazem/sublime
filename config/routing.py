from django.conf.urls import url

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.sessions import SessionMiddlewareStack

from sublime.messager.consumers import MessagerConsumer, VideoCallConsumer
from sublime.notifications.consumers import NotificationsConsumer
# from sublime.notifications.routing import notifications_urlpatterns
# from sublime.messager.routing import messager_urlpatterns

application = ProtocolTypeRouter({
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                url(r'^ws/notifications/$', NotificationsConsumer),
                url(r'^ws/video-call/$', VideoCallConsumer),
                url(r'^ws/(?P<username>[^/]+)/$', MessagerConsumer),
            ])
        ),
    ),
})
