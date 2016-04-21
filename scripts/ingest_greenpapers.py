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

url = 'http://www.thegreenpapers.com/P16/D-PU.phtml'

log = logging.getLogger(__name__)
log.info('Begin greenpapers ingest')

def run():
    response = urllib2.urlopen(url)
    gp_html = response.read().decode('utf-8')

    # Parse the GreenPapers page
    soup = BeautifulSoup(gp_html, 'html.parser')

    # Get the table with the data
    table = soup.find('table')
    #print table

    # Get table rows, delete the first one
    rows = table.find_all('tr')

    # Write out each row
    for row in rows:
        cols = row.find_all('td')
        try:
            assert int(cols[0].text)
        except:
            continue

        text_cols = [c.text for c in cols]
        state_name = text_cols[1]
        if state_name == 'District of Columbia':
            state_name = 'Washington DC'
        if state_name == 'Northern Marianas':
            state_name = 'Northern Mariana Islands'
        state = State.objects.get(name=state_name)
        text_cols = text_cols[2:]

        def numerify(n):
            try: return int(n)
            except: return 0

        numeric_values = map(numerify, text_cols)


        summary, created = DelegateSummary.objects.update_or_create(
            state=state,
            defaults = {
                'sanders_pledged':numeric_values[0],
                'sanders_unpledged':numeric_values[1],
                'available_pledged':numeric_values[2],
                'available_unpledged':numeric_values[3],
                'clinton_pledged':numeric_values[4],
                'clinton_unpledged':numeric_values[5],
                'allocation_pledged':numeric_values[8],
                'allocation_unpledged':numeric_values[9],
            }
        )

