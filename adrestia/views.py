import logging
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Q, Count
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.utils.http import urlquote
from django.views.generic import ListView, TemplateView, FormView, View
from django.views.generic.detail import DetailView
from adrestia.models import *
import sunlight
from crpapi import CRP
import json
from .forms import DelegateForm

log = logging.getLogger(__name__)

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

    def post(self, request, *args, **kwargs):
        # create a form instance and populate it with data from the request:
        form = DelegateForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            #print form.cleaned_data
            state = form.cleaned_data.get('state', '')
            group = form.cleaned_data.get('group', '')
            candidate = form.cleaned_data.get('candidate', '')
            has_opponents = form.cleaned_data.get('has_opponents', '')

            url = reverse('delegate_list', kwargs={'state':state} if state else {})
            url += '?&group={}&candidate={}&has_opponents={}'.format(
                    group.abbr if group else '',
                    candidate.name if candidate else '',
                    has_opponents if has_opponents == True else '',
                    )

            log.info('Returning url: %s', url)
            return HttpResponseRedirect(url)
        else:
            log.error(form.errors)


    def get_context_data(self, **kwargs):
        initial = {}

        context = super(DelegateList, self).get_context_data(**kwargs)

        group = self.request.GET.get('group', None)
        candidate = self.request.GET.get('candidate', None)
        has_opponents = self.request.GET.get('has_opponents', None)

        queryset = self.get_queryset()
        context['dpl_list'] = queryset.filter(group__abbr='DPL')
        context['rep_list'] = queryset.filter(group__abbr='Rep')
        context['sen_list'] = queryset.filter(group__abbr='Sen')
        context['gov_list'] = queryset.filter(group__abbr='Gov')
        context['dnc_list'] = queryset.filter(group__abbr='DNC')
        if hasattr(self, 'state'):
            context['state'] = self.state
            initial['state'] = self.state

        if group: initial['group'] = group
        if candidate: initial['candidate'] = candidate
        if has_opponents: initial['has_opponents'] = has_opponents

        context['form'] = DelegateForm(initial=initial)

        return context

    def get_queryset(self):
        qs = Delegate.objects.all()

        state = self.kwargs.get('state', None)
        group = self.request.GET.get('group', None)
        candidate = self.request.GET.get('candidate', None)
        has_opponents = self.request.GET.get('has_opponents', None)

        log.info("{}, {}, {}".format(state, group, candidate))

        if state and not hasattr(self, 'state'):
            self.state = State.objects.get(state=state.upper())
            qs = qs.filter(state=self.state)

        if group: qs = qs.filter(group__abbr=group)

        if candidate: qs = qs.filter(candidate__name=candidate)

        if has_opponents: qs = qs.exclude(opponents=None)

        qs = qs.select_related(
                'candidate',
                'state_legislator',
                'legislator',
                'group',
                'state')
        qs = qs.prefetch_related('opponents')

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
        queryset = Delegate.objects.filter(pk=pk).select_related(
                'legislator',
                'state_legislator',
                'group',
                'state',
                'candidate')
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
        dtotal = float(Delegate.objects.all().count())
        candidates = PresidentialCandidate.objects.exclude(name="O'Malley")
        candidates = candidates.annotate(dcount=Count('delegate'))
        candidates = candidates.order_by('name')

        pledged = {
            'Clinton':1279,
            'Sanders':1027,
            'Uncommitted':1959,
        }
        ptotal = float(sum(pledged.values()))
        print ptotal

        def series(candidates):
            ret1 = []
            ret2 = []
            for c in candidates:
                cdict1 = {
                    'name':c.name,
                    'scount': c.dcount, 
                    'pcount': pledged[c.name],
                    'data':[
                        int('%2d'%(c.dcount/dtotal*100)),
                        int('%2d'%(pledged[c.name]/ptotal*100)),
                    ]
                }
                cdict2 = cdict1.copy()
                if c.name == 'Clinton':
                    clinton = cdict1.copy()
                elif c.name == 'Sanders':
                    sanders = cdict1.copy()
                cdict2.pop('scount')
                cdict2.pop('pcount')
                ret1.append(cdict1)
                ret2.append(cdict2)
            return ret1, json.dumps(ret2), clinton, sanders
        #series = lambda x:{'name':x.name,'count':c.dcount,'percent':'%2d'%(c.dcount/dtotal*100)}
        series_data, series_json, clinton, sanders = series(candidates)
        print series_data, series_json, clinton, sanders
        ctx = {
                'series_data':series_data,
                'series_json':series_json,
                'clinton':clinton,
                'sanders':sanders
                }

        return render(request, self.template_name, ctx)



