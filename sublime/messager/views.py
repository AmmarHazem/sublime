from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, View
# from django.urls import reverse_lazy
# from channels.layers import get_channel_layer

from sublime.messager.models import Message, notification_handler
from sublime.helpers import ajax_required
from .forms import SelectUserForm


class VideoCallRoom(LoginRequiredMixin, View):
    def get(self, request, caller, calle):
        sender = get_user_model().objects.get(username = caller)
        recipient = get_user_model().objects.get(username = calle)
        message_list = Message.objects.get_conversation(sender = sender, recipient = recipient)
        cxt = {
            'calle' : calle,
            'caller' : caller,
            'message_list' : message_list,
        }
        if request.user == sender:
            cxt['active'] = recipient
        else:
            cxt['active'] = sender
        return render(request, 'messager/video_call.html', cxt)


class StartVidoeCall(LoginRequiredMixin, View):
    def get(self, request):
        form = SelectUserForm()
        form.fields['user'].queryset = get_user_model().objects.filter(is_active = True).exclude(username = request.user.username)
        cxt = {'form' : form}
        return render(request, 'messager/video_call_invite.html', cxt)

    def post(self, request):
        form = SelectUserForm(request.POST)
        if form.is_valid():
            selected_user = form.cleaned_data.get('user')
            notification_handler(
                actor = request.user,
                recipient = selected_user,
                verb = 'B',
                message_text = f'{request.user.username} wants to start a video call with you.',
                key = 'VideoCall',
                room_name = request.user.username,
            )
            return JsonResponse({'success' : True})
        else:
            cxt = {'form' : form}
            return render(request, 'messager/video_call_invite.html', cxt)


class MessagesListView(LoginRequiredMixin, ListView):
    """CBV to render the inbox, showing by default the most recent
    conversation as the active one.
    """
    model = Message
    paginate_by = 10
    template_name = "messager/message_list.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['users_list'] = get_user_model().objects.filter(
            is_active=True).exclude(
                username=self.request.user).order_by('username')
        last_conversation = Message.objects.get_most_recent_conversation(
            self.request.user
        )
        context['active'] = last_conversation.username
        return context

    def get_queryset(self):
        active_user = Message.objects.get_most_recent_conversation(self.request.user)
        return Message.objects.get_conversation(active_user, self.request.user)


class ConversationListView(MessagesListView):
    """CBV to render the inbox, showing an specific conversation with a given
    user, who requires to be active too."""
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['active'] = self.kwargs["username"]
        return context

    def get_queryset(self):
        active_user = get_user_model().objects.get(
            username=self.kwargs["username"])
        return Message.objects.get_conversation(active_user, self.request.user)


@login_required
@ajax_required
@require_http_methods(["POST"])
def send_message(request):
    """AJAX Functional view to recieve just the minimum information, process
    and create the new message and return the new data to be attached to the
    conversation stream."""
    sender = request.user
    recipient_username = request.POST.get('to')
    recipient = get_user_model().objects.get(username=recipient_username)
    message = request.POST.get('message')
    if len(message.strip()) == 0:
        return HttpResponse()

    if sender != recipient and sender.is_authenticated:
        msg = Message.send_message(sender.username, recipient, message)
        return render(request, 'messager/single_message.html', {'message': msg})

    return HttpResponse()


@login_required
@ajax_required
@require_http_methods(["GET"])
def receive_message(request):
    """Simple AJAX functional view to return a rendered single message on the
    receiver side providing realtime connections."""
    message_id = request.GET.get('message_id')
    try:
        message = Message.objects.get(pk=message_id)
    except Message.DoesNotExist:
        print('--- message does not exist')
        message = Message.objects.first()
    return render(request,
                  'messager/single_message.html', {'message': message})
