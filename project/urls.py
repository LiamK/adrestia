from django.conf.urls import url, patterns, include
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from adrestia.views import *

handler400 = 'adrestia.views.error_400'
handler403 = 'adrestia.views.error_403'
handler404 = 'adrestia.views.error_404'
handler500 = 'adrestia.views.error_500'

sitemaps = { 'static': StaticViewSitemap }

urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^$', Home.as_view(), name='home'),
    url(r'^calculator/?$', CalculatorView.as_view(), name='calculator'),
    url(r'^d3/?$', TemplateView.as_view(template_name='adrestia/d3.html'), name='d3'),
    url(r'^nvd3/?$', TemplateView.as_view(template_name='adrestia/nvd3.html'), name='nvd3'),
    #url(r'^titanic.csv/?$', FileView.as_view(), name='titanic'),
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
