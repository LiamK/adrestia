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

from sunlight import openstates

from superdelegates.models import *

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

    # fix in database or in ingest or with source
    Legislator.objects.filter(bioguide_id__in=('Q000024', 'S000275')).update(in_office=False)

    lines = open('SandersDemocrats.csv', 'r').readlines()
    # skip first two lines so DictReader uses them for keys
    lines = lines[2:]
    line_buffer = StringIO.StringIO('\n'.join(lines))

    reader = csv.DictReader(line_buffer, restval='')
    for r in reader:

        name = r.get('Name')
        if not name:
            continue

        state_obj = State.objects.get(name=r.get('State'))
        #if state_obj.state not in ('MA', 'NH', 'VT'):
            #continue;
        state = state_obj.state.lower()

        status = r.get('Status')
        if status.startswith('Serving'): status = 'Serving'

        district = r.get('District')
        level = r.get('Level')
        profile_url = r.get('Sanders Dem Profile')
        notes = r.get('Notes')
        image_url = r.get('img')
        office = r.get('Office')
        try:
            primary_date = tzaware_from_string(r.get('Congressional Primary Date'), '%m/%d/%Y')
        except ValueError:
            primary_date = None


        tmpname = name
        tmpname = tmpname.replace(', Jr.', '')
        tmpname = tmpname.replace(' III', '')
        tmpname = tmpname.replace(' II', '')
        names = tmpname.split()
        firstname = names[0]
        lastname = names[-1:][0]

        if level not in ('State', 'Federal'):
            continue
        if office not in ('House', 'Senate'):
            continue

        # expat changes
        if district == 'VT': district = '0' ## One at-large rep from VT
        if state == 'ma' and firstname == 'Jamie' and lastname == 'Eldridge': firstname = 'James'
        if state == 'ma' and firstname == 'Pat' and lastname == 'Jehlen': firstname = 'Patricia'
        if state == 'vt' and lastname == 'Pollina' and firstname == 'Anthony': chamber = 'upper'

        # sunlight errors
        if state == 'ma' and firstname == 'Mary' and lastname == 'Keefe': firstname = 'Mary S.'
        if state == 'me' and firstname == 'James' and lastname == 'Campbell': firstname = 'James J.'
        if state == 'nh' and firstname == 'Andrew' and lastname == 'White': firstname = 'Andrew A.'
        if state == 'nh' and firstname == 'Andy' and lastname == 'Schmidt': firstname = 'Andrew R.'
        if state == 'nh' and firstname == 'Geoffrey' and lastname == 'Hirsch': firstname = 'Geoffrey D.'
        if state == 'nh' and firstname == 'George' and lastname == 'Sykes': firstname = 'George E.'
        if state == 'nh' and firstname == 'Gilman' and lastname == 'Shattuck': firstname = 'Gilman C.'
        if state == 'nh' and firstname == 'Jane' and lastname == 'Beaulieu': firstname = 'Jane E.'
        if state == 'nh' and firstname == 'Lee' and lastname == 'Oxenham': firstname = 'Lee Walker'
        if state == 'nh' and firstname == 'Marcia' and lastname == 'Moody': firstname = 'Marcia G.'
        if state == 'nh' and firstname == 'Patrick' and lastname == 'Long': firstname = 'Patrick T.'
        if state == 'nh' and firstname == 'Peter' and lastname == 'Bixby': firstname = 'Peter W.'
        if state == 'nh' and firstname == 'Richard' and lastname == 'McNamara': firstname = 'Richard D.'
        if state == 'nh' and firstname == 'Robert' and lastname == 'Cushing': firstname = 'Robert R.'
        if state == 'nh' and firstname == 'Robert' and lastname == 'Theberge': firstname = 'Robert L.'
        if state == 'nh' and firstname == 'Tim' and lastname == 'Smith': firstname = 'Timothy J.'
        if state == 'nh' and firstname == 'Wayne' and lastname == 'Burton': firstname = 'Wayne M.'
        if state == 'vt' and firstname == 'Bill' and lastname == 'Frank': firstname = 'William'
        if state == 'vt' and firstname == 'Linda' and lastname == 'Martin': firstname = 'Linda J.'
        if state == 'vt' and firstname == 'Mary' and lastname == 'Hooper': firstname = 'Mary S.'
        if state == 'vt' and firstname == 'Mollie' and lastname == 'Burke': firstname = 'Mollie S.'
        if state == 'vt' and firstname == 'Steve' and lastname == 'Berry': firstname = 'Steven'
        if state == 'vt' and firstname == 'Warren' and lastname == 'Kitzmiller': firstname = 'Warren F.'
        if state == 'vt' and firstname == 'Tim' and lastname == 'Jerman': firstname = 'Timothy'

        # create candidate here, then tweak below
        new_values = {
            'profile_url':profile_url,
            'notes':notes,
            'image_url':image_url,
            'primary_date':primary_date,
            'level':level,
            'office':office,
            'district':district,
            'status':status,
        }
        # treat the combination of state and name as unique for now, but
        # don't enforce
        candidate, created = Candidate.objects.update_or_create(
                state=state_obj,
                name=name,
                defaults=new_values
                )
        print candidate

        # First go through the incumbents and cross-reference with sunlight
        # openstates dataset to get information
        if status == 'Serving':
            legislators = None
            if level == 'Federal':
                if office == 'House':
                    legislators = Legislator.objects.filter(state=state_obj,
                        district=district, in_office=True)
                elif office == 'Senate':
                    legislators = Legislator.objects.filter(state=state_obj,
                        in_office=True)

            elif level == 'State':
                if office == 'House':
                    legislators = openstates.legislators(
                        state=state,
                        chamber='lower',
                        active=True,
                        last_name=lastname,
                        district=district
                        )
                    sleep(0.5)
                    if not legislators:
                        legislators = openstates.legislators(
                            state=state,
                            chamber='lower',
                            active=True,
                            last_name=lastname,
                            first_name=firstname,
                            )
                        sleep(0.5)
                elif office == 'Senate':
                    legislators = openstates.legislators(
                        state=state,
                        chamber='upper',
                        active=True,
                        last_name=lastname,
                        district=district
                        )
                    sleep(0.5)
                    if not legislators:
                        legislators = openstates.legislators(
                            state=state,
                            chamber='upper',
                            active=True,
                            last_name=lastname,
                            first_name=firstname,
                            )
                        sleep(0.5)
                #if legislators:
                    #legislators = [(l['full_name'],l['district']) for l in legislators]

            if legislators:
                if len(legislators) == 1:
                    leg_obj = legislators[0]
                    print name
                    if type(leg_obj) == dict:
                        # these values are showing up in the json, but are not documented.
                        # id is a duplicate of leg_id that conflicts with # the 'id' in the Django model
                        leg_obj.pop('id', None)
                        leg_obj.pop('csrfmiddlewaretoken', None)
                        leg_obj.pop('nickname', None)
                        leg_obj.pop('office_phone', None)
                        leg_obj.pop('office_address', None)
                        leg_offices = leg_obj.pop('offices', None)

                        # capitalize the state abbreviations
                        leg_obj['state'] = leg_obj['state'].upper()

                        # sunlight fields with '+' char are non-standard, ignore
                        for k in leg_obj.keys():
                            if k.startswith('+'):
                                leg_obj.pop(k, None)

                        leg_obj['created_at'] = tzaware_from_string(leg_obj['created_at'],
                                '%Y-%m-%d %H:%M:%S')
                        leg_obj['updated_at'] = tzaware_from_string(leg_obj['updated_at'],
                                '%Y-%m-%d %H:%M:%S')
                        state_leg, created = StateLegislator.objects.update_or_create(**leg_obj)
                        candidate.state_legislator = state_leg
                        candidate.district = leg_obj['district']

                        # replace old offices with new ones
                        state_leg.offices.clear()
                        for office in leg_offices:
                            ofc = Office.objects.create(**office)
                            state_leg.offices.add(ofc)
                    else:
                        candidate.legislator = leg_obj
                    candidate.save()
                else:
                    print name,
                    print [(l, type(l)) for l in legislators]
                    #log.info(name)
                    #print name, state, district, ' -- ', legislators
            else: 
                print("%s (%s %s) %s %s %s %s %s" % ( name, firstname,
                        lastname, state.upper(), level, office, district, status))
                #log.error("%s (%s %s) %s %s %s %s %s", name, firstname,
                        #lastname, state, level, office, district, status)
                #print name, (firstname, lastname,), state, level, office, district, status
        #print state, r.get('Level'), r.get('Office'), r.get('District'), r.get('Status')
        elif status == 'Candidate':
            pass
        else:
            print "Unknown status: '%s'" % status

    sys.exit(0)

