from django.conf import settings
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from django.views.generic.detail import DetailView
from adrestia.models import *
import sunlight
from crpapi import CRP
import json

def print_dict(d):
    new = {}
    for k, v in d.iteritems():
        if isinstance(v, dict):
            v = print_dict(v)
        new[k.replace('@', '')] = v
    return new

# Create your views here.
class Home(TemplateView):
    template_name = 'adrestia/home.html'

class DelegateList(ListView):
    model = Delegate
    def get_context_data(self, **kwargs):
        context = super(DelegateList, self).get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['dpl_list'] = queryset.filter(group__abbr='DPL')
        context['rep_list'] = queryset.filter(group__abbr='Rep')
        context['sen_list'] = queryset.filter(group__abbr='Sen')
        context['gov_list'] = queryset.filter(group__abbr='Gov')
        context['dnc_list'] = queryset.filter(group__abbr='DNC')
        if hasattr(self, 'state'):
            context['state'] = self.state
        return context

    def get_queryset(self):
        queryset = Delegate.objects.all()

        state = self.kwargs.get('state', None)
        if state and not hasattr(self, 'state'):
            self.state = State.objects.get(state=state.upper())
            queryset = queryset.filter(state=self.state)

        queryset = queryset.select_related(
            'candidate', 'state_legislator', 'legislator', 'group', 'state')

        return queryset

class DelegateDetail(DetailView):
    model = Delegate
    def get_context_data(self, **kwargs):
        CRP.apikey = settings.CRP_API_KEY
        context = super(DelegateDetail, self).get_context_data(**kwargs)

        if not self.object.legislator:
            return context

        try:
            member_profile = CRP.memPFDprofile.get(
                cid=self.object.legislator.crp_id, cycle='2014')
            member_profile = print_dict(member_profile)
            member_profile = member_profile['attributes']
        except:
            member_profile = None

        try:
            contributors = CRP.candContrib.get(
                cid=self.object.legislator.crp_id, cycle='2016')
            contributors = print_dict(contributors)
            meta_contributors = contributors['attributes']
            contributors = [print_dict(c) for c in contributors['contributor']]
        except:
            contributors = None
            meta_contributors = None

        context['member_profile'] = member_profile
        context['contributors'] = contributors
        context['meta_contributors'] = meta_contributors
        return context

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        queryset = Delegate.objects.filter(pk=pk).select_related('legislator',
                'group', 'state', 'candidate')
        return queryset

class CandidateList(ListView):
    model = Candidate

class CandidateDetail(DetailView):
    model = Candidate
