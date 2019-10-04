from django.conf.urls import url

from sublime.messager import views

app_name = 'messager'
urlpatterns = [
    url(r'^$', views.MessagesListView.as_view(), name='messages_list'),
    url(r'^video-call/$', views.StartVidoeCall.as_view(), name = 'start-video-call'),
    url(r'^video-call/(?P<caller>[\w.@+-]+)/(?P<calle>[\w.@+-]+)/$', views.VideoCallRoom.as_view(), name = 'video-call-room'),
    url(r'^send-message/$', views.send_message, name='send_message'),
    url(r'^receive-message/$',
        views.receive_message, name='receive_message'),
    url(r'^(?P<username>[\w.@+-]+)/$', views.ConversationListView.as_view(),
        name='conversation_detail'),
]
