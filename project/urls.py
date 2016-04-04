"""adrestia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from adrestia.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', Home.as_view(), name='home'),
    url(r'^delegates/?$', DelegateList.as_view(), name='delegate_list'),
    url(r'^delegates/(?P<pk>[0-9]+)', DelegateDetail.as_view(), name='delegate_detail'),
    url(r'^candidates/?$', CandidateList.as_view(), name='candidate_list'),
    url(r'^candidates/(?P<pk>[0-9]+)', CandidateDetail.as_view(),
        name='candidate_detail'),
]
