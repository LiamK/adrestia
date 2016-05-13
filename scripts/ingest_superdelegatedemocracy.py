#!/usr/bin/python
from time import sleep, strptime, mktime
import datetime
import sys
import urllib2
from bs4 import BeautifulSoup
from bs4.diagnose import diagnose
import csv
import re
import StringIO
import logging
import pytz
import pprint

from sunlight import openstates

from adrestia.models import *

# set encoding
reload(sys)
sys.setdefaultencoding('utf8')

log = logging.getLogger(__name__)
#log.setFormatter(colorlog.ColoredFormatter(
    #'%(log_color)s%(levelname)s:%(name)s:%(message)s'))

def tzaware_from_string(date, fmt='%m/%d/%Y'):
    dt = datetime.datetime.fromtimestamp(mktime(strptime(date, fmt)))
    return pytz.utc.localize(dt)

def run():
    state_slugs = [(s, slugify(s.name)) for s in 
        State.objects.exclude(name='Unassigned')]

    for state, slug in state_slugs:
        if slug == 'washington-dc': slug = 'district-of-columbia'
        filename = 'data/superdelegatedemocracy.com/states/' + slug
        state_file = open(filename, 'r')
        html = state_file.read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('h1', class_='stat-title')
        print title.text 
        delegate_rows = soup.find_all('tr', class_='delegate-table')
        for d in delegate_rows:
            cols = d.find_all('td')
            name = cols[0].text
            social_media_urls = cols[3].find_all('a')
            if not social_media_urls:
                continue

            try:
                delegate = Delegate.objects.get(name__iexact=name)
                print '\t', name 
            except Delegate.DoesNotExist:
                name = name.strip()
                log.warn("Could not find '%s'", name)
                simplename = re.sub(r',*\s*[JS]r\.', '', name)
                simplename = re.sub(r'^Mayor\s*', '', simplename)
                simplename = re.sub(r'^Hon\.*\s*', '', simplename)
                simplename = re.sub(r'Wiliiams', 'Williams', simplename)
                simplename = re.sub(r'Ceasar', 'Caesar', simplename)
                lastname = simplename.split()[-1]
                firstname = simplename.split()[0]
                try:
                    delegate = Delegate.objects.get(
                            name__istartswith=firstname,
                            name__iendswith=lastname,
                            )
                except Delegate.DoesNotExist:
                    log.warn("Could not find first/last name '%s/%s'",
                            firstname, lastname)
                    try:
                        delegate = Delegate.objects.get(
                                name__iendswith=lastname,
                                )
                    except Delegate.DoesNotExist:
                        log.error("Could not find last name '%s'",
                                lastname)
                        continue
                    except Delegate.MultipleObjectsReturned:
                        log.error("Multiple Objects, last name '%s'", lastname)
                        continue

            facebook_id = twitter_id = youtube_url = None
            for s in social_media_urls:
                url = s.get('href')
                print '\t', url

                m = re.search(
                    r'https?://(www.)?facebook.com/(\w#!/)?(pages/)?(([\w-]/)*)?(?P<id>[\w.-]+)', url)
                if m:
                    facebook_id = m.group('id')

                m = re.search(r'^(https*://twitter.com/|@)([A-Za-z0-9_]+)$',
                        url)
                if m: 
                    try:
                        twitter_id = m.group(2)
                        assert len(twitter_id) <= 15
                    except AssertionError:
                        log.error('Twitter id too long')

                m = re.search(r"https*://[\w.]*youtube.com/(.*)", url)
                if m:
                    youtube_url = url

            print '\t', facebook_id, twitter_id, youtube_url

            if not delegate.facebook_id and facebook_id:
                delegate.facebook_id = facebook_id
            if not delegate.twitter_id and twitter_id:
                delegate.twitter_id = twitter_id
            #if not delegate.youtube_url and youtube_url:
                #delegate.youtube_url = youtube_url

            delegate.save()
    sys.exit()
