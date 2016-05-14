#!/usr/bin/python
# -*- coding: utf-8 -*-

from time import sleep, strptime, mktime
import datetime
import sys
import urllib2
import json
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
    for c in Candidate.objects.filter(name__endswith=' '):
        c.name = c.name.strip()
        c.save()

    c = Candidate.objects.get(name='Bob Sweere')
    c.facebook_id = '100010700328351'
    c.save()

    c = Candidate.objects.get(name='Pramila Jayapal')
    c.twitter_id = 'PramilaJayapal'
    c.image = None
    c.save()

#    c = Candidate.objects.get(name='Martin Quezada')
#    c.name = 'Martín Quezada'
#    c.save()
#
#    c = Candidate.objects.get(name='Ed Vargas')
#    c.name = 'Edwin Vargas'
#    c.save()
#
#    c = Candidate.objects.get(name='Michael Trout')
#    c.name = 'W. Michael Trout'
#    c.save()
#
#    c = Candidate.objects.get(name='Julian Bell')
#    c.name = 'Dr. Julian Bell'
#    c.save()
#
#    c = Candidate.objects.get(name='Joe Neal')
#    c.name = 'Joseph Neal'
#    c.save()
#
#    c = Candidate.objects.get(name='Rosanna Gabaldon')
#    c.name = 'Rosanna Gabaldón'
#    c.save()
#
#    c = Candidate.objects.get(name='Bao Ngyuen')
#    c.name = 'Bao Nguyen'
#    c.save()
#
#    c = Candidate.objects.get(name='Luis Sepulveda')
#    c.name = 'Luis Sepúlveda'
#    c.save()
#
#    c = Candidate.objects.get(name='Jesse Sabaih')
#    c.name = 'Jesse Sbaih'
#    c.save()
#
    c = Candidate.objects.get(name='Pierre Frantz').delete()


#    for c in Candidate.objects.all():
#        if c.winner:
#            c.primary_win = True
#            c.save()


