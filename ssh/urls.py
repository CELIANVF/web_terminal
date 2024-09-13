# ssh/urls.py:

from django.urls import path

from ssh import consumers
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ssh_gui/', views.ssh_gui, name='ssh_gui'),
    path('ssh_gui/<str:command>/', views.ssh_gui, name='ssh_gui'),
]