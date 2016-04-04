#!/usr/bin/python
import sys
import urllib2
from time import sleep
from django.db.models import Q
from django.conf import settings
from bs4 import BeautifulSoup
from bs4.diagnose import diagnose
import csv
import re
import pprint
from StringIO import StringIO
from sunlight import openstates

from superdelegates.models import *

# set encoding
reload(sys)
sys.setdefaultencoding('utf8')

def run():
    # get the ones that aren't federal or the state Governor.
    delegates = Delegate.objects.exclude(Q(group__abbr='Sen') |
        Q(group__abbr='Rep') | Q(group__abbr='Gov'))
    print 'Count delegates who are not Reps,Sens,Govs', delegates.count()
    match = []
    nomatch = []
    multimatch = []
    for d in delegates[:50]:
        name = d.name
        name = name.replace(', Jr.', '')
        name = name.replace(' III', '')
        name = name.replace(' II', '')
        names = name.split()
        firstname = names[0]
        lastname = names[-1:][0]
        try:
            # these are state legislators, not our own (fed) Legislator object
            legislators = openstates.legislators(
                state=d.state.state.lower(),
                party='Democratic',
                first_name=firstname,
                last_name=lastname,
                )
            print name
            sleep(0.5)
            if legislators and len(legislators) == 1:
                legislator = legislators[0]
                match.append("%s: %s" % (name, legislator['full_name']))
            elif legislators:
                multimatch.append(
                    "%s: %s" % (name, [f['full_name'] for f in legislators]))
            else:
                nomatch.append(name)
                continue;
        except:
            raise

    print "Match", len(match)
    print pprint.pprint(match)
    print "No match", len(nomatch)
    print pprint.pprint(nomatch)
    print "Multi match", len(multimatch)
    print pprint.pprint(multimatch)
