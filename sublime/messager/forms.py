from django import forms
from django_select2.forms import Select2Widget
from django.contrib.auth import get_user_model


class SelectUserForm(forms.Form):
    user = forms.ModelChoiceField(queryset = get_user_model().objects.all(), widget = Select2Widget(attrs = {'class' : 'form-control'}), to_field_name = 'username')
