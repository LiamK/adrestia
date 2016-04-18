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

from adrestia.models import *

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
        names1 = name.split()
        names2 = name.split(' ', 1)
        firstname1 = names1[0]
        lastname1 = names1[-1:][0]
        firstname2 = names2[0]
        lastname2 = names2[-1:][0]
        try:
            legislator = Legislator.objects.get(
                (Q(firstname__startswith=firstname1) &
                Q(lastname__startswith=lastname1)) |
                (Q(firstname__startswith=firstname2) &
                Q(lastname__startswith=lastname2)) |
                (Q(nickname__startswith=firstname1) &
                Q(lastname__startswith=lastname1)))
            print legislator
            d.legislator = legislator
            d.save()
        except:
#        except Legislator.DoesNotExist:
#            print '%s does not exists' % d
#        except Legislator.MultipleObjectsReturned:
#            print '%s multiple objects' % d
            try:
                legislators = Legislator.objects.filter(
		    Q(state=d.state.state) &
                    (Q(lastname=lastname1) |
                     Q(lastname=lastname2))
                )
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
