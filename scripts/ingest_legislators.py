#!/usr/bin/python
import sys
import urllib2
import csv
from StringIO import StringIO

from superdelegates.models import *

# set encoding
reload(sys)
sys.setdefaultencoding('utf8')

url = 'http://unitedstates.sunlightfoundation.com/legislators/legislators.csv'

def run():
    response = urllib2.urlopen(url)
    Legislator.objects.all().delete()
    legislators = StringIO(response.read().decode('utf-8'))
    reader = csv.DictReader(legislators)
    for row in reader:
        legislator = Legislator(**row)
        legislator.save()
        print legislator
