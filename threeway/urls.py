from django.conf.urls import *
from django.conf.urls import url, patterns, include
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$',
        TemplateView.as_view(template_name='threeway/index.html'),
        name='threeway'),
]
