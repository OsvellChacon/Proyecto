from django.urls import path
from . import views
from auditlog.models import LogEntry

urlpatterns = [
    path("", views.auditoria, name='auditoria'),
]