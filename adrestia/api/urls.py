from django.conf.urls import url, include
from rest_framework import routers

from adrestia.api import views

router = routers.DefaultRouter()
router.register(r'candidate', views.CandidateViewSet, base_name='candidate')
router.register(r'state', views.StateViewSet, base_name='state')

urlpatterns = [
    url(r'^', include(router.urls)),
]

