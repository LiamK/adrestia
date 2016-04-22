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
from django.conf.urls import url, patterns, include
from django.contrib import admin
from django.views.generic import TemplateView
from adrestia.views import *

handler400 = 'adrestia.views.error_400'
handler403 = 'adrestia.views.error_403'
handler404 = 'adrestia.views.error_404'
handler500 = 'adrestia.views.error_500'

urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^$', Home.as_view(), name='home'),
    url(r'^chart/?$', ChartView.as_view(), name='chart'),
    url(r'^chart/(?P<state>[A-Za-z-]{2,2})/?$', ChartView.as_view(), name='state_chart'),
    url(r'^about/?$', TemplateView.as_view(template_name='adrestia/about.html'), name='about'),
    url(r'^privacy_policy/?$', TemplateView.as_view(template_name='adrestia/privacy_policy.html'), name='privacy_policy'),
    url(r'^delegates/?$', DelegateList.as_view(), name='delegate_list'),
    url(r'^delegates/(?P<state>[A-Za-z-]{2,2})/?$', DelegateList.as_view(),name='delegate_list'),
    url(r'^delegates/(?P<pk>[0-9]+)/?$', DelegateDetail.as_view(), name='delegate_detail'),
    url(r'^candidates/?$', CandidateList.as_view(), name='candidate_list'),
    url(r'^candidates/(?P<state>[A-Za-z]{2,2})/?$', CandidateList.as_view(),name='candidate_list'),
    url(r'^candidates/(?P<pk>[0-9]+)/?$', CandidateDetail.as_view(),
        name='candidate_detail'),
    url(r'^thankyou/?$',
        TemplateView.as_view(template_name='adrestia/thankyou.html'),
        name='thankyou'),
    url(r'^api/', include('adrestia.api.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
