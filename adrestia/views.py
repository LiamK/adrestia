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
        context['dpl_list'] = context.get('delegate_list').filter(group__abbr='DPL')
        context['rep_list'] = context.get('delegate_list').filter(group__abbr='Rep')
        context['sen_list'] = context.get('delegate_list').filter(group__abbr='Sen')
        context['gov_list'] = context.get('delegate_list').filter(group__abbr='Gov')
        context['dnc_list'] = context.get('delegate_list').filter(group__abbr='DNC')
        return context

class DelegatesByState(ListView):
    template_name = 'adrestia/delegate_list.html'
    def get_context_data(self, **kwargs):
        context = super(DelegatesByState, self).get_context_data(**kwargs)
        context['state'] = self.state
        context['dpl_list'] = context.get('delegate_list').filter(group__abbr='DPL')
        context['rep_list'] = context.get('delegate_list').filter(group__abbr='Rep')
        context['sen_list'] = context.get('delegate_list').filter(group__abbr='Sen')
        context['gov_list'] = context.get('delegate_list').filter(group__abbr='Gov')
        context['dnc_list'] = context.get('delegate_list').filter(group__abbr='DNC')
        return context
    def get_queryset(self):
        # need the state in the context 
        self.state = State.objects.get(state=self.kwargs.get('state').upper())
        #queryset = Delegate.objects.filter(Q(state=self.state) | Q(group__abbr='DPL'))
        queryset = Delegate.objects.filter(Q(state__state=self.state))
        return queryset

class DelegateDetail(DetailView):
    model = Delegate
    def get_context_data(self, **kwargs):
        CRP.apikey = settings.CRP_API_KEY
        context = super(DelegateDetail, self).get_context_data(**kwargs)

        if not self.object.legislator:
            return context

        member_profile = CRP.memPFDprofile.get(
            cid=self.object.legislator.crp_id, cycle='2014')
        member_profile = print_dict(member_profile)
        member_profile = member_profile['attributes']

        contributors = CRP.candContrib.get(
            cid=self.object.legislator.crp_id, cycle='2016')
        contributors = print_dict(contributors)
        meta_contributors = contributors['attributes']
        contributors = [print_dict(c) for c in contributors['contributor']]

        #import pprint
        #print pprint.pprint(member_profile)
        #print pprint.pprint(meta_contributors)
        #print pprint.pprint(contributors)
        context['member_profile'] = member_profile
        context['contributors'] = contributors
        context['meta_contributors'] = meta_contributors
        return context

class CandidateList(ListView):
    model = Candidate

class CandidateDetail(DetailView):
    model = Candidate
