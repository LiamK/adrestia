#!/usr/bin/python
# Sonic DNS 208.201.224.11
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

url = 'http://api.berniecrats.net/?fmt=json'

def run():
    response = urllib2.urlopen(url)
    berniecrats = json.loads(response.read().decode('utf-8')).get('berniecrats')

    statuses = berniecrats[0].get('status')
    offices = berniecrats[1].get('offices')
    candidates = berniecrats[2].get('candidates')

    status_dict = list_to_dict(statuses)
    office_dict = list_to_dict(offices)

    multiple_legislators = []
    missing_legislators = []

    data = []
    found = []
    not_found = []
    possible_match = []

    for c in candidates:
        #print c.get('firstName'), c.get('lastName')
        first_name = c.get('firstName').strip()
        last_name = c.get('lastName').strip()
        name = '%s %s' % (first_name, last_name)
        state = State.objects.get(state=c.get('state'))
        party = c.get('partyCode')
        serving = c.get('isIncumbent')
        level = get_level(c)
        office = get_office(c, office_dict)
        district = get_district(c)
        website_url = c.get('website')
        endorsement_url = c.get('infoUrl')
        endorsement_text = c.get('infoLink')
        primary_win = get_null_bool(c.get('electPrimary'))
        general_win = get_null_bool(c.get('electGeneral'))
        #updated = tzaware_from_string(c.get('lastUpdate'), '%Y-%m-%d %H:%M:%S')
        #created = tzaware_from_string(c.get('createDate'), '%Y-%m-%d %H:%M:%S')
        status = c.get('status')
        notes = c.get('statusMsg')
        running = status == "0"
        facebook_id = sanitize_facebook(c.get('facebook'))
        twitter_id = sanitize_twitter(c.get('twitter'))

        if name == 'Philip Cornell': name = 'Phil Cornell'
        if name == 'Dave Zuckerman': name = 'David Zuckerman'
        if party == 'VP D': party = 'VPP'

        data.append([
            name, party, state.state, level, office, district, twitter_id, facebook_id])

        # treat the combination of state and name as unique for now, but
        # don't enforce
        candidate = None
        try:
            candidate = Candidate.objects.get(
                state=state,
                name=name,
            )
            found.append('%s %s' % (candidate.state.state, candidate.name))
        except Candidate.DoesNotExist:
            try:
                min_fname = first_name.split()[0]
                min_lname = re.sub(r',*\s*[JS]r\.\s*', '', last_name)
                candidate = Candidate.objects.get(
                    state=state,
                    name__startswith=min_fname,
                    name__endswith=min_lname,
                )
                found.append('%s %s' % (candidate.state.state, candidate.name))
            except Candidate.DoesNotExist:
                try:
                    min_lname = re.sub(r',*\s*[JS]r\.\s*', '', last_name)
                    candidate = Candidate.objects.get(
                        state=state,
                        name__endswith=min_lname,
                    )
                    possible_match.append('%s %s (%s %s ?)' % (
                        candidate.state.state,
                        candidate.name,
                        first_name,
                        last_name))
                except Candidate.DoesNotExist:
                    not_found.append(state.state + ' ' + name)

    #print matrix_to_string(data)

#        if level not in ('State', 'Federal'):
#            continue
#        if office not in ('House', 'Senate'):
#            continue

        sname = state.state.lower()
        district = fix_district(district)
        first_name, last_name = fix_names(sname, first_name, last_name)

        # create candidate here, then tweak below
        new_values = {
            #'profile_url':None,
            #'donate_url':None,
            #'image_url':None,
            #'primary_date':None,
            #'status':status,
            'notes':notes,
            'first_name':first_name,
            'last_name':last_name,
            'website_url':website_url,
            'twitter_id':twitter_id,
            'facebook_id':facebook_id,
            'endorsement_url':endorsement_url,
            'endorsement_text':endorsement_url,
            'level':level,
            'office':office,
            'district':district,
            'serving':serving,
            'running':running,
            'primary_win':primary_win,
            'general_win':general_win,
            'party':party,
        }

        if candidate:
            updated = False
            created = False
            candidate.mismatch = []
            for k,v in new_values.items():
                # if missing value, then merge
                if not getattr(candidate, k):
                    setattr(candidate, k, v)
                    updated = True
                # values are identical then continue
                elif getattr(candidate, k) == v:
                    pass
                # twitter_id values are identical (case insensitive)
                elif k == 'twitter_id' and getattr(candidate, k).lower() == v.lower():
                    pass
                # values are different
                elif v:
                    candidate.mismatch.append("\t.%s: '%s' != '%s'" % (k, getattr(candidate, k), v))
        else:
            candidate = Candidate(
                state=state,
                name=name,
                **new_values
                )
            created = True

        if hasattr(candidate, 'mismatch') and candidate.mismatch:
            print candidate.name,
            if candidate.legislator:
                print "[%s %s %s]" % ('Federal',
                        candidate.legislator.title, candidate.legislator.district),
            elif candidate.state_legislator:
                print "[%s %s %s]" % ('State',
                        candidate.state_legislator.chamber, candidate.state_legislator.district),
            print
            print '\n'.join(candidate.mismatch)


        # Okay, now save it
        log.debug('Candidate: %s', candidate)
        candidate.save()

        # First go through the incumbents and cross-reference with sunlight
        # openstates dataset to get information
        if candidate.serving and level in ('Federal', 'State') and office in ('House', 'Senate'):
            legislators = None
            if level == 'Federal':
                if office == 'House':
                    legislators = Legislator.objects.filter(state=state,
                        district=district, in_office=True)
                elif office == 'Senate':
                    legislators = Legislator.objects.filter(state=state,
                        in_office=True)

            elif level == 'State':
                if office == 'House':
                    legislators = openstates.legislators(
                        state=state.state,
                        chamber='lower',
                        active=True,
                        last_name=last_name,
                        district=district
                        )
                    sleep(0.5)
                    if not legislators:
                        legislators = openstates.legislators(
                            state=state.state,
                            chamber='lower',
                            active=True,
                            last_name=last_name,
                            first_name=first_name,
                            )
                        sleep(0.5)
                elif office == 'Senate':
                    legislators = openstates.legislators(
                        state=state.state,
                        chamber='upper',
                        active=True,
                        last_name=last_name,
                        district=district
                        )
                    sleep(0.5)
                    if not legislators:
                        legislators = openstates.legislators(
                            state=state.state,
                            chamber='upper',
                            active=True,
                            last_name=last_name,
                            first_name=first_name,
                            )
                        sleep(0.5)
                #if legislators:
                    #legislators = [(l['full_name'],l['district']) for l in legislators]

            if legislators:
                if len(legislators) == 1:
                    leg_obj = legislators[0]
                    if type(leg_obj) == dict:
                        # these values are showing up in the json, but are not documented.
                        # id is a duplicate of leg_id that conflicts with # the 'id' in the Django model
                        leg_obj.pop('id', None)
                        leg_obj.pop('nimsp_candidate_id', None)
                        leg_obj.pop('nimsp_id', None)
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

                        leg_id = leg_obj.pop('leg_id')

                        state_leg, created = StateLegislator.objects.update_or_create(leg_id=leg_id, defaults=leg_obj)
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
                    multiple_legislators.append( {
                        'candidate':candidate,
                        'matches':[(l, type(l)) for l in legislators]
                        } )
                    #print [(l, type(l)) for l in legislators]
                    #log.info(name)
                    #print name, state, district, ' -- ', legislators
            else: 
                missing_legislators.append("%s (%s %s) %s %s %s %s %s" % (
                    name, first_name, last_name, state.state.upper(), level, office, district, status))
                print("%s (%s %s) %s %s %s %s %s" % ( name, first_name,
                        last_name, state.state.upper(), level, office, district, status))
                #log.error("%s (%s %s) %s %s %s %s %s", name, firstname,
                        #lastname, state, level, office, district, status)
                #print name, (firstname, lastname,), state, level, office, district, status
        #print state, r.get('Level'), r.get('Office'), r.get('District'), r.get('Status')

    print "These need to be processed manually"
    print "Multiples"
    print pprint.pprint(multiple_legislators)
    print "Missing from Sunlight data"
    print pprint.pprint(missing_legislators)


    db_candidates = ['%s %s' % (c.state.state, c.name) for c in Candidate.objects.all()]
    db_only = list(set(db_candidates) - set(found))

    print 'Found', len(found)
    pprint.pprint(sorted(found))
    print 'Possible Match', len(possible_match)
    pprint.pprint(sorted(possible_match))
    print 'Not Found', len(not_found)
    pprint.pprint(sorted(not_found))
    print 'DB Only', len(db_only)
    pprint.pprint(sorted(db_only))

    # create dictionary with state keys and lists of candidates as items
    # for candidates only in database
    db_only_dict = {}
    for c in db_only:
        state, name = c.split(' ',1)
        try:
            db_only_dict[state].append(name)
        except KeyError:
            db_only_dict[state] = []
            db_only_dict[state].append(name)

    # create dictionary with state keys and lists of candidates as items
    # for candidates not found in database
    not_found_dict = {}
    for c in not_found:
        state, name = c.split(' ',1)
        try:
            not_found_dict[state].append(name)
        except KeyError:
            not_found_dict[state] = []
            not_found_dict[state].append(name)

    # print out by state
    for s in State.objects.exclude(name='Unassigned'):
        try:
            col1 = db_only_dict[s.state]
        except KeyError:
            col1 = []

        try:
            col2 = not_found_dict[s.state]
        except KeyError:
            col2 = []
        if not col1 and not col2:
            continue
        print
        print s.name
        print '-' * len(s.name)

        print '{:<10}'.format('DB ONLY'), ', '.join(col1)
        print '{:<10}'.format('NOT FOUND'), ', '.join(col2)
        print matrix_to_string([[col1], [col2]])


def matrix_to_string(matrix, header=None):
    """
    Return a pretty, aligned string representation of a nxm matrix.

    This representation can be used to print any tabular data, such as
    database results. It works by scanning the lengths of each element
    in each column, and determining the format string dynamically.

    @param matrix: Matrix representation (list with n rows of m elements).
    @param header: Optional tuple or list with header elements to be displayed.
    """
    if type(header) is list:
        header = tuple(header)
    lengths = []
    if header:
        for column in header:
            lengths.append(len(column))
    for row in matrix:
        for column in row:
            i = row.index(column)
            column = str(column)
            cl = len(column)
            try:
                ml = lengths[i]
                if cl > ml:
                    lengths[i] = cl
            except IndexError:
                lengths.append(cl)

    lengths = tuple(lengths)
    format_string = ""
    for length in lengths:
        format_string += "%-" + str(length) + "s "
    format_string += "\n"

    matrix_str = ""
    if header:
        matrix_str += format_string % header
    for row in matrix:
        matrix_str += format_string % tuple(row)

    return matrix_str

def tzaware_from_string(date, fmt='%m/%d/%Y'):
    dt = datetime.datetime.fromtimestamp(mktime(strptime(date, fmt)))
    return pytz.utc.localize(dt)

# change structure from list of dict to dict
def list_to_dict(array):
    ret = {}
    for d in array:
        k,v = d.items()[0]
        ret[k] = v
    return ret

def get_level(c):
    if int(c.get('office')) <= 100:
        level = 'Federal'
    elif int(c.get('office')) <= 200:
        level = 'State'
    elif int(c.get('office')) <= 300:
        level = 'County'
    elif int(c.get('office')) <= 400:
        level = 'City'
    elif int(c.get('office')) <= 500:
        level = 'Neighborhood'
    else:
        raise ValueError('Unrecognized office value: %s', c.get('office'))
    return level

def get_office(c, office_dict):
    if int(c.get('office')) in (1, 103):
        office = 'Senate'
    elif int(c.get('office')) in (2, 104):
        office = 'House'
    else:
        office = office_dict[c.get('office')]
    return office

def get_district(c):
    # if the office is 'US Senate' or 'US Representative'
    if int(c.get('office')) <= 2:
        m = re.search(r'(\d+)', c.get('district'))
        if m:
            return m.group(1)
    return re.sub(r'[,\s]*District[s,\s]*', ' ', c.get('district')).strip()

def sanitize_facebook(facebook_id):
    if not facebook_id: return None
    m = re.search(r'(?P<id>\d{7,})', facebook_id)
    if m: return m.group('id')
    m = re.search(
        r'https?://(www.)?facebook\.com/(\w#!/)?(pages/)?(([\w-]/)*)?(?P<id>[\w.-]+)', facebook_id)
    if m: return m.group('id')
    log.error('Bad facebook id: %s', facebook_id)
    return facebook_id

def sanitize_twitter(twitter_id):
    if not twitter_id: return None
    try:
        twitter_id = re.sub(r'\?.*', '', twitter_id)
        m = re.search(
            r'^(https*://twitter.com/|@)([A-Za-z0-9_]+)$', twitter_id)
        if m: 
            twitter_id = m.group(2)
        assert len(twitter_id) <= 15
    except AssertionError:
        log.warn('Twitter id too long, using first: %s', twitter_id)
        try:
            twitter_id = sanitize_twitter(twitter_id.split()[0])
            assert len(twitter_id) <= 15
        except:
            log.error('Twitter id still too long: %s', twitter_id)
    return twitter_id

def get_null_bool(val):
    if not val:
        return None
    if val == 'won':
        return True
    if val == 'lost':
        return False
    raise ValueError('Bad value: %s', val)

def fix_district(district):
    if district == 'VT': district = '0' ## One at-large rep from VT
    if district == '11th Suffolk': district = 'Suffolk 11'
    if district == 'Middlesex and Worcester': district = 'Middlesex & Worcester'
    if district == 'Chittenden 6-7': district = 'Chittenden-6-7'
    if district == '2nd Middlesex': district = 'Second Middlesex'
    if district == "Hawai'i, 5th": district = "Hawai'i 5"
    if district == 'Middlesex': district = 'Second Middlesex'
    return district

def fix_names(sname, first_name, last_name):
    if sname == 'ma' and first_name == 'Jamie' and last_name == 'Eldridge': first_name = 'James'
    if sname == 'ma' and first_name == 'Pat' and last_name == 'Jehlen': first_name = 'Patricia'
    if sname == 'vt' and last_name == 'Pollina' and first_name == 'Anthony': chamber = 'upper'

    # sunlight errors
    if sname == 'ma' and first_name == 'Mary' and last_name == 'Keefe': first_name = 'Mary S.'
    if sname == 'me' and first_name == 'James' and last_name == 'Campbell': first_name = 'James J.'
    if sname == 'nh' and first_name == 'Andrew' and last_name == 'White': first_name = 'Andrew A.'
    if sname == 'nh' and first_name == 'Andy' and last_name == 'Schmidt': first_name = 'Andrew R.'
    if sname == 'nh' and first_name == 'Geoffrey' and last_name == 'Hirsch': first_name = 'Geoffrey D.'
    if sname == 'nh' and first_name == 'George' and last_name == 'Sykes': first_name = 'George E.'
    if sname == 'nh' and first_name == 'Gilman' and last_name == 'Shattuck': first_name = 'Gilman C.'
    if sname == 'nh' and first_name == 'Jane' and last_name == 'Beaulieu': first_name = 'Jane E.'
    if sname == 'nh' and first_name == 'Lee' and last_name == 'Oxenham': first_name = 'Lee Walker'
    if sname == 'nh' and first_name == 'Marcia' and last_name == 'Moody': first_name = 'Marcia G.'
    if sname == 'nh' and first_name == 'Patrick' and last_name == 'Long': first_name = 'Patrick T.'
    if sname == 'nh' and first_name == 'Peter' and last_name == 'Bixby': first_name = 'Peter W.'
    if sname == 'nh' and first_name == 'Richard' and last_name == 'McNamara': first_name = 'Richard D.'
    if sname == 'nh' and first_name == 'Robert' and last_name == 'Cushing': first_name = 'Robert R.'
    if sname == 'nh' and first_name == 'Robert' and last_name == 'Theberge': first_name = 'Robert L.'
    if sname == 'nh' and first_name == 'Tim' and last_name == 'Smith': first_name = 'Timothy J.'
    if sname == 'nh' and first_name == 'Wayne' and last_name == 'Burton': first_name = 'Wayne M.'
    if sname == 'vt' and first_name == 'Bill' and last_name == 'Frank': first_name = 'William'
    if sname == 'vt' and first_name == 'Linda' and last_name == 'Martin': first_name = 'Linda J.'
    if sname == 'vt' and first_name == 'Mary' and last_name == 'Hooper': first_name = 'Mary S.'
    if sname == 'vt' and first_name == 'Mollie' and last_name == 'Burke': first_name = 'Mollie S.'
    if sname == 'vt' and first_name == 'Steve' and last_name == 'Berry': first_name = 'Steven'
    if sname == 'vt' and first_name == 'Warren' and last_name == 'Kitzmiller': first_name = 'Warren F.'
    if sname == 'vt' and first_name == 'Tim' and last_name == 'Jerman': first_name = 'Timothy'
    return first_name, last_name
