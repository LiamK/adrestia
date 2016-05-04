import logging
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, Http404, FileResponse
from django.db.models import Q, Count, Sum, Case, When
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.utils.http import urlquote
from django.views.generic import ListView, TemplateView, FormView, View
from django.views.generic.detail import DetailView
from adrestia.models import *
import sunlight
from crpapi import CRP
import json
from .forms import DelegateForm, CandidateForm

log = logging.getLogger(__name__)

def print_dict(d):
    new = {}
    for k, v in d.iteritems():
        if isinstance(v, dict):
            v = print_dict(v)
        new[k.replace('@', '')] = v
    return new

def error_400(request, exception, template_name='adrestia/400.html'):
    return render(request, template_name)
def error_403(request, exception, template_name='adrestia/403.html'):
    return render(request, template_name)
def error_404(request, exception, template_name='adrestia/404.html'):
    return render(request, template_name)
def error_500(request, template_name='adrestia/500.html'):
    return render(request, template_name)


class Home(TemplateView):
    template_name = 'adrestia/home.html'

class CalculatorView(TemplateView):
    template_name = 'adrestia/calculator.html'

class FileView(View):
    def get(self, request):
        response = FileResponse(open('titanic.csv', 'rb'))
        return response


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

        qs.votes = qs.aggregate(count=Sum('vote_value'))

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
    def post(self, request, *args, **kwargs):
        # create a form instance and populate it with data from the request:
        form = CandidateForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            #print form.cleaned_data
            state = form.cleaned_data.get('state', '')
            level = form.cleaned_data.get('level', '')
            office = form.cleaned_data.get('office', '')

            url = reverse('candidate_list', kwargs={'state':state} if state else {})
            url += '?&level={}&office={}&'.format(
                    level if level else '',
                    office if office else ''
                    )

            log.info('Returning url: %s', url)
            return HttpResponseRedirect(url)
        else:
            log.error(form.errors)


    def get_context_data(self, **kwargs):
        initial = {}

        context = super(CandidateList, self).get_context_data(**kwargs)

        level = self.request.GET.get('level', None)
        office = self.request.GET.get('office', None)

        if hasattr(self, 'state'):
            context['state'] = self.state
            initial['state'] = self.state

        if level: initial['level'] = level
        if office: initial['office'] = office

        context['form'] = CandidateForm(initial=initial)

        return context

    def get_queryset(self):
        qs = Candidate.objects.all()

        state = self.kwargs.get('state', None)
        level = self.request.GET.get('level', None)
        office = self.request.GET.get('office', None)

        log.info("{}, {}, {}".format(state, level, office))

        if state and not hasattr(self, 'state'):
            self.state = State.objects.get(state=state.upper())
            qs = qs.filter(state=self.state)

        if level: qs = qs.filter(level=level)

        if office: qs = qs.filter(office=office)

        qs = qs.select_related(
                'state_legislator',
                'legislator',
                'state')

        return qs


class CandidateDetail(DetailView):
    model = Candidate
    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        queryset = Candidate.objects.filter(pk=pk).select_related('legislator',
                'state_legislator', 'state')
        return queryset

def get_chart_context(state_abbr=None):
        # Get the super delegates
        delegates = Delegate.objects.all()
        states = State.objects.exclude(name='Unassigned').order_by('name')

        try:
            if state_abbr:
                state = State.objects.get(state=state_abbr)
            else:
                state = None
        except State.DoesNotExist:
            raise Http404

        if state:
            delegates = delegates.filter(state__state=state)
        dtotal = float(delegates.count())

        # get the annotated presidential candidates
        if state:
            candidates = PresidentialCandidate.objects.exclude(name="O'Malley").annotate(
                dcount=Count(
                    Case(
                        When(
                            delegate__state__state=state,
                            then=1,
                        )
                    )
                )
            )

        else:
            candidates = PresidentialCandidate.objects.exclude(name="O'Malley")
            candidates = candidates.annotate(dcount=Count('delegate'))

        # ordering is important 
        candidates = candidates.order_by('id')


        # Get the pledged delegate counts
        pledged = DelegateSummary.objects.all()
        if state:
            pledged = pledged.filter(state__state=state)
        pledged = pledged.aggregate(
                Sanders=Sum('sanders_pledged'),
                Clinton=Sum('clinton_pledged'),
                Uncommitted=Sum('available_pledged'),
                )
        try:
            ptotal = float(sum(pledged.values()))
            assert ptotal > 0
        except AssertionError:
            raise Http404

        def series(candidates):
            ret1 = []
            ret2 = []
            clinton = {}
            sanders = {}
            for c in candidates:
                # This may be removed, depends on Uncommitted/No Endorsement
                hack_name = c.name.replace(' ', '_')
                cdict1 = {
                    'name':c.name,
                    'scount': c.dcount, 
                    'pcount': pledged[hack_name],
                    'data':[
                        int('%2d'%(c.dcount/dtotal*100)),
                        int('%2d'%(pledged[hack_name]/ptotal*100)),
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
        series_data, series_json, clinton, sanders = series(candidates)

        ctx = {
                'series_data':series_data,
                'series_json':series_json,
                'clinton':clinton,
                'sanders':sanders,
                'state':state,
                'states':states,
                }
        return ctx

class ChartView(View):
    def get(self, request, **kwargs):
        state = self.kwargs.get('state', None)
        if state:
            template_name = 'adrestia/state_chart.html'
        else:
            template_name = 'adrestia/chart.html'
        ctx = get_chart_context(state)
        return render(request, template_name, ctx)

