import logging
import datetime
import django_filters
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.cache import cache
from django.utils.encoding import force_text

from rest_framework import viewsets, filters
from rest_framework.settings import api_settings
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_csv import renderers

from adrestia.models import Candidate, State
from adrestia.api.serializers import CandidateSerializer, StateSerializer

class CandidateViewSet(viewsets.ReadOnlyModelViewSet):
    """ Bernie Candidates"""
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [renderers.CSVRenderer]
    queryset = Candidate.objects.all().order_by('name')
    serializer_class = CandidateSerializer

class StateViewSet(viewsets.ReadOnlyModelViewSet):
    """ States"""
    queryset = State.objects.all().order_by('name')
    serializer_class = StateSerializer
