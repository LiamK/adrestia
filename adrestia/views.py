from django.conf import settings
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
