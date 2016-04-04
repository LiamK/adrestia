#!/usr/bin/python
import sys
import urllib2
from django.db.models import Q
from bs4 import BeautifulSoup
from bs4.diagnose import diagnose
import csv
import re
import pprint
from StringIO import StringIO

from superdelegates.models import *

# set encoding
reload(sys)
sys.setdefaultencoding('utf8')

def run():
#    legislators = Legislator.objects.all()
#    for legislator in legislators:
#        try:
#            delegate = Delegate.objects.get(
#                name__startswith=legislator.firstname,
#                name__endswith=legislator.lastname)
#            print "%s == %s" % (legislator, delegate)
#        except:
#            pass

    delegates = Delegate.objects.filter(Q(group__abbr='Sen') |
        Q(group__abbr='Rep'))
    print 'Count Reps and Sens', delegates.count()
    nomatch = []
    multimatch = []
    for d in delegates:
        name = d.name
        name = name.replace(', Jr.', '')
        name = name.replace(' III', '')
        names = name.split()
        firstname = names[0]
        lastname = names[-1:][0]
        try:
            legislator = Legislator.objects.get(
                (Q(firstname__startswith=firstname) &
                Q(lastname__startswith=lastname)) |
                (Q(nickname__startswith=firstname) &
                Q(lastname__startswith=lastname)))
            print legislator
            d.legislator = legislator
            d.save()
        except:
            try:
                legislators = Legislator.objects.filter(
                    lastname=lastname, state=d.state.state)
                if legislators.count() == 1:
                    legislator = legislators[0]
                    print legislator
                    d.legislator = legislator
                    d.save()
                else:
                    assert legislators
                    multimatch.append((d, legislators))
            except:
                nomatch.append(d)
    print "No match", len(nomatch)
    print pprint.pprint(nomatch)
    print "Multi match", len(multimatch)
    print pprint.pprint(multimatch)
