from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Q, Count
from django.shortcuts import render
from django.views.generic import ListView, TemplateView, FormView, View
from django.views.generic.detail import DetailView
from adrestia.models import *
import sunlight
from crpapi import CRP
import json
from .forms import DelegateForm

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

class DelegateList(ListView, FormView):
    model = Delegate
    form_class = DelegateForm

    def post(self, request, *args, **kwargs):
        # create a form instance and populate it with data from the request:
        form = DelegateForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print form.cleaned_data
            state = form.cleaned_data.get('state', None)
            group = form.cleaned_data.get('group', None)
            candidate = form.cleaned_data.get('candidate', None)
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            url = '/delegates/'
            if state:
                url += state
            if group or candidate:
                url += '?'
            if group:
                url += '&group=%s' % group
            if candidate:
                url += '&candidate=%s' % candidate
            return HttpResponseRedirect(url)
        else:
            print form.errors


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
        qs = Delegate.objects.all()
        print dir(self.request)

        state = self.kwargs.get('state', None)
        group = self.request.GET.get('group', None)
        candidate = self.request.GET.get('candidate', None)

        print 'State is: %s' % state
        if state and not hasattr(self, 'state'):
            self.state = State.objects.get(state=state.upper())
            print 'Setting state to State: %s' % self.state
            qs = qs.filter(state=self.state)

        if group: qs = qs.filter(group__abbr=group)

        if candidate: qs = qs.filter(candidate__name=candidate)

        qs = qs.select_related('candidate', 'state_legislator', 'legislator', 'group', 'state')

        return qs

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
                'state_legislator', 'group', 'state', 'candidate')
        return queryset

class CandidateList(ListView):
    model = Candidate
    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        queryset = Candidate.objects.all().select_related('legislator',
                'state_legislator', 'state')
        return queryset

class CandidateDetail(DetailView):
    model = Candidate

class ChartView(View):
    template_name = 'adrestia/chart.html'
    def get(self, request):
        total_delegates = float(Delegate.objects.all().count())
        candidates = PresidentialCandidate.objects.exclude(name="O'Malley").annotate(
                dcount=Count('delegate')).order_by('name')
        data = [
                {
                    'name':c.name,
                    'count':"%2d" % (c.dcount / total_delegates * 100)
                }
            for c in candidates
        ]
        ctx = { 'data': data }

        return render(request, self.template_name, ctx)



