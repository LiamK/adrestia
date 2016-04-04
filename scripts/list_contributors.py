#!/usr/bin/python
import sys
import urllib2
import csv
import re
from StringIO import StringIO
from django.conf import settings
from crpapi import CRP, CRPApiError

from superdelegates.models import *

# set encoding
reload(sys)
sys.setdefaultencoding('utf8')

def run():
    CRP.apikey = settings.CRP_API_KEY
    legislators = Legislator.objects.filter(crp_id__isnull=False)[:2]
    for legislator in legislators:
        print legislator
        try:
            print CRP.candContrib.get(cid=legislator.crp_id, cycle='2014')
        except:
            pass
