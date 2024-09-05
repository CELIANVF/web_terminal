# ssh/forms.py

from django import forms

class loginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    host = forms.CharField(label='Host', max_length=100)
    port = forms.IntegerField(label='Port')

