from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class MessagerConfig(AppConfig):
    name = 'sublime.messager'
    verbose_name = _('Messager')
