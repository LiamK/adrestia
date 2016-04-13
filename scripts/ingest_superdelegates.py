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

#    # fix in database or in ingest or with source
#    Legislator.objects.filter(bioguide_id__in=('Q000024', 'S000275')).update(in_office=False)
#
#    lines = open('SuperDelegateContactSheet.csv', 'r').readlines()
#    # skip first two lines so DictReader uses them for keys
#    lines = lines[2:]
#    line_buffer = StringIO.StringIO('\n'.join(lines))
#
    reader = csv.DictReader(open('SuperDelegateContactSheet.csv', 'r'), restval='')

    multiple_legislators = []
    missing_legislators = []

    for r in reader:
        group = r.get('Group')
        if not 'Gov' in group and not 'DPL' in group:
            continue
        name = r.get('Delegate by First Name')
        if not name:
            continue

        try:
            state_obj = State.objects.get(state=r.get('State'))
            state = state_obj.state
        except:
            print r.get('State')

        webform_url = ''
        email = r.get('Email Address')
        if not '@' in email:
            webform_url = email
            email = ''
        else:
            try:
                email = re.search(r'([^@\s]+@[^@\s]+\.[^@\s]+)', email).group(1)
            except:
                raise
                email = ''

        useless = r.get('Other Methods of Contact')
        phone = r.get('Phone Number ')
        phone = re.sub(r'(011/ )', '011/', phone)
        phone = re.search(r'([-0-9\/()]+)', phone)
        if phone:
            phone = phone.group(1)
        else:
            phone = ''


        twitter_id = r.get('Twitter') or ''
        facebook_id = r.get('Facebook')
        if facebook_id:
            #facebook_id = re.sub(r"https*://facebook.com/", '', facebook_id)
            try:
                facebook_id = re.search(r"https*://[\w.]*facebook.com/(.*)/\?fref=ts",
                    facebook_id).group(1)
            except:
                facebook_id = ''

        if twitter_id:
            twitter_id = re.sub(r"https*://twitter.com/", '', twitter_id)


        # create candidate here, then tweak below
        new_values = {
            'twitter_id':twitter_id,
            'facebook_id':facebook_id,
            'webform_url':webform_url,
            'phone':phone,
            'email':email,
        }

        if set(new_values.values()) == set(['']):
            continue

        try:
            delegate = Delegate.objects.get(name=name)
        except Delegate.DoesNotExist:
            delegate = '%s not found' % name
            continue

        print 'Updating %s' % delegate
        for k,v in new_values.items():
            setattr(delegate, k, v)
        delegate.save()

        #print '\t', '\t'.join([state, name, email, phone, webform_url, facebook_id, twitter_id])

