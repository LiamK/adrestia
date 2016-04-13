#!/usr/bin/python
import sys
import urllib2
from bs4 import BeautifulSoup
from bs4.diagnose import diagnose
import csv
import re

from adrestia.models import *

WIKIPEDIA_PREFIX = 'http://en.wikipedia.org'
url = WIKIPEDIA_PREFIX + '/wiki/List_of_Democratic_Party_superdelegates,_2016'

def run():
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
        delegate, state, group, cd, candidate = r.find_all('td')
        # These are the <sup> (footnote) tags
        candidate_sup = candidate.find('sup')
        group_sup = group.find('sup')

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
        state = state[:2] # cut off extraneous footnote, e.g. "DA[note 1]"
        delegate = delegate.replace('[3]', '') # cut off extraneous footnote, e.g. "DA[note 1]"
        group = re.sub(r'\[\d+\]', '', group)
        candidate = re.sub(r'\s*\[\d+\]\s*', '', candidate)
        group = group.replace('.', '')

        dnc_group, created = DNCGroup.objects.get_or_create(abbr=group,
                defaults = {'name':'default'} )
        candidate, created = PresidentialCandidate.objects.get_or_create(name=candidate)
        dstate, created = State.objects.get_or_create(state=state,
                defaults = {'name':'default'})
        delegate, created = Delegate.objects.update_or_create(
            name=delegate,
            state=dstate,
            defaults = {
                'url':delegate_url,
                'group':dnc_group,
                'candidate':candidate,
            }
        )
        # if not created, update with potentially new values
        if not created:
            delegate.url = delegate_url
            delegate.state = dstate
            delegate.group = dnc_group
            delegate.candidate = candidate
        print delegate

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

