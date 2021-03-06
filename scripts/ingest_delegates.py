#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import sys
import pprint
import urllib2
from bs4 import BeautifulSoup
from bs4.diagnose import diagnose
import csv
import re

from django.db.utils import IntegrityError

from adrestia.models import *

WIKIPEDIA_PREFIX = 'http://en.wikipedia.org'
url = WIKIPEDIA_PREFIX + '/wiki/List_of_Democratic_Party_superdelegates,_2016'

log = logging.getLogger(__name__)
log.info('Begin super delegate ingest')

def run():
    # Get set of db objects, to compare with new objects added
    new_delegate_set = set()
    created_delegate_set = set()
    db_delegate_set = {"%s %s" % (d.state.state, d.name) for d in Delegate.objects.all()}

    response = urllib2.urlopen(url)
    wiki_html = response.read().decode('utf-8')

    # Parse the Wikipedia page
    soup = BeautifulSoup(wiki_html, 'html.parser')

    # Get the table with the data
    table = soup.find('table', class_='sortable')

    # Get table rows, delete the first one
    rows = table.find_all('tr')[1:]

    # Write the first row
    #writer = csv.writer(sys.stdout)
    #writer.writerow([
    #        'delegate',
    #        'delegate_url',
    #        'state',
    #        'group',
    #        'group_sup_url',
    #        'group_sup_text',
    #        'candidate',
    #        'candidate_sup_url',
    #        'candidate_sup_text',
    #    ])

    # Write out each row
    for r in rows:
        delegate, state, group, candidate = r.find_all('td')
        # These are the <sup> (footnote) tags
        candidate_sup = candidate.find('sup')
        group_sup = group.find('sup')
        delegate_html = delegate

        try:
            candidate_sup_text = candidate_sup.a.get('href', None)
            candidate_sup_num = re.sub(r'[\[\]]', '', candidate_sup.a.text)
            candidate_sup_text = re.sub(r'^#', '', candidate_sup_text)
            ref = soup.find(id=candidate_sup_text)
            cite = ref.find('cite')
            candidate_sup_url = cite.find('a')['href']
            candidate_sup_text = cite.find('a').text
        except:
            candidate_sup_text = None
            candidate_sup_url = None

        try:
            group_sup_text = group_sup.a.get('href', None)
            group_sup_num = re.sub(r'[\[\]]', '', group_sup.a.text)
            group_sup_text = re.sub(r'^#', '', group_sup_text)
            ref = soup.find(id=group_sup_text)
            cite = ref.find('cite')
            group_sup_url = cite.find('a')['href']
            group_sup_text = cite.find('a').text
        except:
            group_sup_text = None
            group_sup_url = None

        if delegate.a:
            delegate_url = WIKIPEDIA_PREFIX + delegate.a['href']
        else:
            delegate_url = None

        delegate, state, group, candidate = [x.text for x in (delegate, state, group, candidate)]
        candidate = candidate.strip()
        # the Wikipedia editors keep changing this!
        if candidate.startswith('None'):
            candidate = 'Uncommitted'
        state = state[:2] # cut off extraneous footnote, e.g. "DA[note 1]"
        if state == u'—':
            state = 'UA'
        delegate = re.sub(r'\[[\d]+\]', '', delegate) # cut off extraneous footnote, e.g. "DA[note 1]"
        # replace '.' in 'Rep.', and [note...] stuff
        group = re.sub(r'(\[[A-Za-z\s\d]+\]|\.*)', '', group)
        # remove [notes]
        candidate = re.sub(r'\s*\.*\s*\[[a-z\d]+\]\s*', '', candidate)
        if candidate not in ('Sanders', 'Clinton', 'Uncommitted', "O'Malley"):
            log.error("Candidate '%s' not recognized...skipping", candidate)
            continue

        # dnc_group, created = DNCGroup.objects.get_or_create(abbr=group,
            # defaults = {'name':'default'} )
        #candidate, created = PresidentialCandidate.objects.get_or_create(name=candidate)
        #dstate, created = State.objects.get_or_create(state=state,
                #defaults = {'name':'default'})
        dnc_group = DNCGroup.objects.get(abbr=group)
        candidate = PresidentialCandidate.objects.get(name=candidate)
        dstate = State.objects.get(state=state)
        try:
            log.debug('%s (%s)', delegate, state)
            delegate, created = Delegate.objects.update_or_create(
                name=delegate,
                state=dstate,
                defaults = {
                    'url':delegate_url,
                    'group':dnc_group,
                    'candidate':candidate,
                }
            )
            new_delegate_set.add("%s %s" % (state, delegate.name))
            if created:
                log.warn('Created: %s', delegate)
                created_delegate_set.add("%s %s" % (state, delegate.name))
        except IntegrityError, e:
            log.error("%s: %s", e, delegate)
            continue
        except Delegate.DoesNotExist:
            log.error("Does not exist: %s", delegate)
            continue
        except Delegate.MultipleObjectsReturned:
            log.error("Multiple Objects Returned: %s (%s)", delegate, state)
            continue

        # hopefully these wont't change
        if group_sup_text:
            footnote, created = Footnote.objects.update_or_create(
                id=group_sup_num,
                defaults={
                    'url':group_sup_url,
                    'text':group_sup_text,
                }
            )
            delegate.footnotes.add(footnote)

        if candidate_sup_text:
            footnote, created = Footnote.objects.update_or_create(
                    id=candidate_sup_num,
                    defaults={
                        'url':candidate_sup_url,
                        'text':candidate_sup_text,
                    }
                    )
            delegate.footnotes.add(footnote)

    print 'CREATED %d NEW SUPERDELATES' % len(created_delegate_set)
    log.warn('db_delegate_set: %s', len(db_delegate_set))
    pprint.pprint(created_delegate_set)

    # This should be the same as created
    print 'NEW not in DB'
    pprint.pprint(new_delegate_set - db_delegate_set)

    print 'DB but not NEW -- REMOVE'
    pprint.pprint(db_delegate_set - new_delegate_set)

    log.warn('symmetric difference')
    pprint.pprint(db_delegate_set ^ new_delegate_set)
