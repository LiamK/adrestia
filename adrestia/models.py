from __future__ import unicode_literals

import logging
import hashlib
import requests
import imghdr

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.core.cache import cache
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.files.base import ContentFile
from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from django.utils.html import format_html
from django.utils.text import slugify

log = logging.getLogger(__name__)

"""
Party abbreviations
"Minnesota Democratic-Farmer-Labor Party", "DFL",

"A Connecticut Party", "AC",
"American First Coalition", "AF",
"American Heritage Party", "AH",
"American Independent Pty", "AI",
"Alaskan Independence", "AK",
"American Constitution", "AN",
"American", "AM",
"Blue Enigma Party", "BE",
"Builders Party", "BD",
"Boston Tea", "BT",
"Better Schools", "B ",
"Buchanan Reform", "BR",
"Concerned Citizens", "CC",
"Centrist Party", "CE",
"Citizens First", "CF",
"Connecticut Independent", "CI",
"Cool Moose", "CM",
"Constitutional", "CN",
"Concerns of People", "CP",
"Conservative", "C ",
"Constitution", "CS",
"CT for Lieberman", "CL",
"DC Statehood Green Party", "DC",
"Democrat", "D ",
"Ecology Party of Florida", "EP",
"End Suffolk Legislature", "E ",
"Fair", "FA",
"Free Energy Party", "FE",
"Fusion Independent", "F ",
"Freedom", "FR",
"Friends United", "Fr",
"Farmers & Small Business", "FB",
"Freedom Socialist", "FS",
"Family Values Party", "FV",
"Green Coalition Party", "GC",
"Greens No To War", "GN",
"Green", "GR",
"Grass Roots Party", "G ",
"Healthcare Party", "HC",
"Home Protection", "HP",
"Heartquake '08", "HQ",
"Independent American", "IA",
"Independent Fusion", "IF",
"Independent Grassroots", "IL",
"Independent Green", "GI",
"Independent", "I ",
"Independence", "IN",
"Integrity Party", "IT",
"Independent Party", "IP",
"Independent Party of DE", "ID",
"Independent Party of HI", "IH",
"Independent-Progressive", "IR",
"Ind. Save Our Children", "IC",
"Liberal", "L ",
"Looking Back Party", "LO",
"Labor and Farm", "LA",
"Libertarian", "LB",
"Long Island First", "LF",
"Legalize Marijuana", "LM",
"Louisiana Taxpayers", "LT",
"Liberty Union", "LU",
"Liberty Union/Progressiv", "LP",
"Maryland Independent Par", "MI",
"Marijuana Party", "MJ",
"Make Marijuana Legal", "MM",
"Mountain Party", "MN",
"Marijuana Reform Party", "MR",
"New Alliance", "NA",
"Nebraska", "NE",
"New", "N ",
"No Home Heat Tax", "NH",
"Natural Law Party", "NL",
"New Mexico Independent P", "NM",
"No New Taxes", "NT",
"No", "NO",
"Non-Partisan", "NP",
"No Party Affiliation", "NF",
"No Party Designation", "ND",
"Objectivist", "OB",
"One Earth", "OE",
"Open", "OP",
"128 District", "OT",
"Other", "AO",
"Pacific", "PC",
"Pacific Green", "PN",
"Patriot Party", "PP",
"Pacifist", "PA",
"Personal Choice", "PH",
"Petitioning Candidate", "PE",
"Party of Ethics & Tradit", "P ",
"Peace and Freedom", "PF",
"Peace and Justice", "PJ",
"Pro Life Conservative", "PL",
"Populist", "PO",
"Peace Party of Oregon", "PX",
"Progressive", "PG",
"Prohibition", "PR",
"Preserve Our Town", "PS",
"Party for Socialism and", "SX",
"Property Tax Cut", "PT",
"People of Vermont", "PV",
"Protect Working Families", "PW",
"Republican", "R ",
"Resource Party", "RS",
"Randolph for Congress", "RC",
"Restore Justice-Freedom", "RJ",
"Reform Minnesota", "RM",
"Reform Party", "RF",
"Republican Moderate", "RD",
"Right to Life", "RL",
"School Choice", "SC",
"Socialism", "SL",
"Save Seniors", "SS",
"Socialist Equality", "SE",
"Save Medicare", "S ",
"Socialist", "SO",
"Socialist USA", "SU",
"Star Tax Cut", "ST",
"Student First", "SF",
"Socialist Workers Party", "SW",
"To Be Determined", "TB",
"The Better Life", "BL",
"Tax Cut", "T ",
"Tax Cut Now", "TC",
"The Go", "TG",
"Term Limits", "TL",
"Timesizing", "TS",
"United Citizen", "UC",
"Unaffiliated", "UN",
"Unenrolled", "U ",
"United", "UD",
"U.S. Taxpayers Party", "TX",
"Unity", "UY",
"Veterans Party", "VT",
"Vermont Grassroots", "GS",
"Voice of the People", "V ",
"Voters Rights Party", "VP",
"Working Class Party", "WC",
"Working Families", "WF",
"West Side Neighbors", "WN",
"We the People", "WP",
"Workers for Vermont", "WV",
"Workers World", "WW",
"Yes", "YS",

"""

def make_digest(instance, filename):
    """ Make digest filename, with leading Candidate id number """
    ext = filename.split('.')[-1]
    m = hashlib.md5()
    m.update(filename)
    filename = "%s.%s" % (m.hexdigest(), ext)
    return filename


class Zip(models.Model):
    code = models.CharField(max_length=5, unique=True)
    state = models.CharField(max_length=2)
    city = models.CharField(max_length=16)
    location = models.PointField(null=True, blank=True)

    class Meta:
        ordering = ('code',)

    def __unicode__(self):
        return unicode(self.code)

class State(models.Model):
    state = models.CharField(max_length=2)
    name = models.CharField(max_length=36)
    fips_state = models.CharField(max_length=2, default='ZZ')
    census_region_name = models.CharField(max_length=12, default='ZZ')
    primary_date = models.DateField(null=True, blank=True)
    general_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ('state',)

    def __unicode__(self):
        return unicode(self.state)

class DNCGroup(models.Model):
    abbr = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=36, null=True)

    class Meta:
        ordering = ('abbr',)
        verbose_name_plural = 'DNC Groups'

    def __unicode__(self):
        return unicode(self.name)

class PresidentialCandidate(models.Model):
    name = models.CharField(max_length=36, unique=True)

    class Meta:
        ordering = ('id',)

    def __unicode__(self):
        return unicode(self.name)

class Candidate(models.Model):
    LEVELS = [
            (None, 'Any Level'),
            ('Federal', 'Federal'),
            ('State', 'State'),
            ('County', 'County'),
            ('City', 'City'),
            ('Neighborhood', 'Neighborhood'),
            ]
    OFFICES = [
            (None, 'Any Office'),
            ('Senate', 'Senate'),
            ('House', 'House'),
            ('Governor', 'Governor'),
            ('Lt. Governor', 'Lt. Governor'),
            ('Secretary of State', 'Secretary of State'),
            ('County Council', 'County Council'),
            ('Mayor', 'Mayor'),
            ('City Council', 'City Council'),
            ('Town Representative', 'Town Representative'),
                ('County Recorder', 'County Recorder'),
                ('County Commissioner', 'County Commissioner'),
                ('County Auditor', 'County Auditor'),
                ('County Legislature', 'County Legislature'),
                ('County Supervisor', 'County Supervisor'),
                ('City-County Council', 'City-County Council'),
                ('Alderman', 'Alderman'),
                ('Alderwoman', 'Alderwoman'),
                ('Justice of the Peace', 'Justice of the Peace'),
                ('Central Committee', 'Central Committee'),
                ('Neighborhood Council', 'Neighborhood Council'),
                ('Surrogate', 'Surrogate'),
                ('Freeholder', 'Freeholder'),
            ]
    PARTIES = [
            ('D',   'Democrat'),
            ('G',   'Green'),
            ('GI',  'Independent Green'),
            ('DFL', 'Minnesota Democratic-Farmer-Labor Party'),
            ('IR',  'Independent-Progressive'),
            ('IP',  'Independent Party'),
            ('PF',  'Peace and Freedom'),
            ('R',   'Republican'),
            ('VPP', 'Vermont Progressive Party'),
            ('UN',  'Unaffiliated'),
        ]
    PARTY_DICT = dict(PARTIES)

    name = models.CharField(max_length=36)
    first_name = models.CharField(null=True, blank=True, max_length=36)
    last_name = models.CharField(null=True, blank=True, max_length=36)
    state = models.ForeignKey(State, null=True)
    level = models.CharField(max_length=24, choices=LEVELS, null=True)
    office = models.CharField(max_length=24, choices=OFFICES, null=True)
    district = models.CharField(max_length=36, null=True, blank=True,
        help_text='Fed or State house district name or number, Junior '
                  'Seat or Senior Seat for Fed Senate, City for Mayor')
    status = models.CharField(max_length=24, null=True, blank=True)
    serving = models.BooleanField(
        help_text='Check this candidate is the incumbent')
    running = models.BooleanField(
        help_text='Running for office or re-election')
    primary_win = models.NullBooleanField(
        help_text='Check this if candidate has won their primary')
    general_win = models.NullBooleanField(
        help_text='Check this if candidate has won their general election')
    winner = models.BooleanField(default=False,
        help_text='Check this if candidate has won their election')
    notes = models.TextField(null=True, blank=True, 
        help_text='Additional information displayed on page')
    primary_date = models.DateField(null=True, blank=True,
        help_text='Deprecated.  This field is ignored. See State.')
    legislator = models.ForeignKey('Legislator', to_field='bioguide_id',
        null=True, blank=True,
        help_text='Enter Legislator if this candidate is the incumbent')
    state_legislator = models.ForeignKey('StateLegislator',
        to_field='leg_id', null=True, blank=True,
        help_text='Enter State Legislator if this candidate is the incumbent')
    party = models.CharField(max_length=3, choices=PARTIES,
        null=True, blank=True,
        help_text='See for abbreviations: http://abcnews.go.com/Politics/party-abbreviations/story?id=10865978')

    facebook_id = models.CharField(max_length=64, null=True, blank=True,
        help_text='Use Facebook ID, not URL')
    twitter_id = models.CharField(max_length=64, null=True, blank=True,
        help_text='Use Twitter ID, not URL')
    profile_url = models.URLField(max_length=500, null=True, blank=True,
        help_text='Expat profile URL')
    website_url = models.URLField(max_length=500, null=True, blank=True)
    donate_url = models.URLField(max_length=500, null=True, blank=True)
    endorsement_url = models.URLField(max_length=500, null=True, blank=True)
    endorsement_text = models.CharField(max_length=500, null=True, blank=True)
    webform_url = models.URLField(max_length=500, null=True, blank=True,
        help_text='Enter URL of web form if available')
    email = models.EmailField(null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True,
        help_text='Enter image URL here and the image will be uploaded')
    image = models.ImageField(null=True, blank=True, upload_to=make_digest,
        help_text='Enter a local image file here to upload')
    created = models.DateTimeField(auto_now_add=True, help_text='Created')
    updated = models.DateTimeField(auto_now=True, help_text='Updated')


    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return unicode(self.name)

    def title_and_name(self, additional=False):
        if self.serving:
            if self.legislator:
                ret = unicode("%s. %s" % (self.legislator.title, self.name))
                if additional:
                    ret += unicode(" (%s %s)" % (self.state, self.legislator.district))
            elif self.state_legislator:
                if self.state_legislator.chamber == 'upper': title = 'State Sen'
                elif self.state_legislator.chamber == 'lower': title = 'State Rep'
                ret = unicode("%s. %s" % (title, self.name))
                if additional:
                    ret += unicode(" (%s %s)" % (self.state, self.state_legislator.district))
            else:
                log.error('Candidate serving but no sunlight record: %s', self)
                ret = unicode("%s" % (self.name))
        else:
            ret = unicode("%s" % (self.name))
            if additional:
                ret += unicode(" (%s)" % (self.state))
        return ret

    def copy_image(self):
        if not self.image:
            if self.image_url:
                url = self.image_url
            elif self.state_legislator and self.state_legislator.photo_url:
                url = self.state_legislator.photo_url
            else:
                return

            if url:
                filename = url.split('/')[-1]
                #print 'filename', filename
                #log.debug('Copying %s from %s', filename, url)
                image_file = NamedTemporaryFile(delete=True)
                try:
                    req = requests.get(url)
                    req.raise_for_status()
                    image_file.write(req.content)
                    image_file.flush()
                    # imghdr.what() tests the image data contained in the file named by
                    # filename, and returns a string describing the image type.
                    # If optional h is provided, the filename is ignored and h is
                    # assumed to contain the byte stream to test.
                    assert imghdr.what(image_file.name)
                except requests.exceptions.RequestException, e:
                    log.error('%s', e)
                    return
                except AssertionError:
                    log.error('Not an image file: %s, %s', filename, url)
                    return

                self.image.save(filename, File(image_file))

    def get_delegate(self):
        try:
            if self.level == 'Federal': 
                delegate = Delegate.objects.get(
                    ~Q(name=self.name),
                    state=self.state,
                    legislator__district=self.district,
                    )
                return delegate
        except Delegate.DoesNotExist:
            pass
            log.debug('No delegate found for %s', self)
        except Delegate.MultipleObjectsReturned:
            log.warn('Multiple matches for %s', self)

        try:
            if self.level == 'State':
                delegate = Delegate.objects.get(
                    ~Q(name=self.name),
                    state=self.state,
                    state_legislator__district=self.district,
                    )
                return delegate
        except Delegate.DoesNotExist:
            pass
            log.debug('No delegate found for %s', self)
        except Delegate.MultipleObjectsReturned:
            log.warn('Multiple matches for %s', self)

        return None


class Footnote(models.Model):
    url = models.URLField(max_length=500, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    class Meta:
        ordering = ('id',)

    def __unicode__(self):
        return unicode("%s (%s)" % (self.text, self.url))

class Delegate(models.Model):
    name = models.CharField(max_length=64, unique=True)
    url = models.URLField(max_length=500, null=True, blank=True)
    state = models.ForeignKey(State)
    group = models.ForeignKey(DNCGroup)
    candidate = models.ForeignKey(PresidentialCandidate)
    footnotes = models.ManyToManyField(Footnote)
    legislator = models.ForeignKey('Legislator', to_field='bioguide_id',
            null=True, blank=True)
    state_legislator = models.ForeignKey('StateLegislator', to_field='leg_id',
            null=True, blank=True)
    opponents = models.ManyToManyField('Candidate')
    facebook_id = models.CharField(max_length=64, null=True, blank=True)
    twitter_id = models.CharField(max_length=64, null=True, blank=True)
    webform_url = models.URLField(max_length=500, null=True, blank=True)
    website_url = models.URLField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=16, null=True, blank=True)
    fax = models.CharField(max_length=16, null=True, blank=True)
    address = models.CharField(max_length=256, null=True, blank=True)
    vote_value = models.DecimalField(decimal_places=1, max_digits=2, default=1.0)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
            return unicode("%s" % (self.name))

    def get_opponents(self):
        if self.legislator:
            qs = Candidate.objects.filter(state=self.state, district=self.legislator.district)
            qs = qs.exclude(name__contains=self.legislator.lastname)
            return qs
        elif self.state_legislator:
            qs = Candidate.objects.filter(state=self.state, district=self.state_legislator.district)
            # hack to prevent matching on self!
            # only a problem if two candidates with the same last name 
            # are running for the same seat
            qs = qs.exclude(name__contains=self.state_legislator.last_name)
            return qs
        else:
            return None

    def title_and_name(self, additional=False):
        if self.legislator:
            ret = unicode("%s. %s" % (self.group.abbr, self.name))
            if additional:
                ret += unicode(" (%s %s)" % (self.state, self.legislator.district))
        elif self.state_legislator:
            ret = unicode("%s. %s" % (self.group.abbr, self.name))
            if additional:
                ret += unicode(" (%s %s)" % (self.state, self.state_legislator.district))
        else:
            ret = unicode("%s %s" % (self.group.abbr, self.name))
            if additional:
                ret += unicode(" (%s)" % (self.state))
        return ret

class Legislator(models.Model):
    title = models.CharField(max_length=3, null=True, blank=True)
    firstname = models.CharField(max_length=36, null=True, blank=True)
    middlename = models.CharField(max_length=36, null=True, blank=True)
    lastname = models.CharField(max_length=36, null=True, blank=True)
    name_suffix = models.CharField(max_length=24, null=True, blank=True)
    nickname = models.CharField(max_length=24, null=True, blank=True)
    party = models.CharField(max_length=1, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    district = models.CharField(max_length=24, null=True, blank=True, db_index=True)
    in_office = models.BooleanField()
    gender = models.CharField(max_length=1, null=True, blank=True)
    phone = models.CharField(max_length=16, null=True, blank=True)
    fax = models.CharField(max_length=16, null=True, blank=True)
    website = models.URLField(max_length=500, null=True, blank=True)
    webform = models.URLField(max_length=500, null=True, blank=True)
    congress_office = models.CharField(max_length=128, null=True, blank=True)
    bioguide_id = models.CharField(unique=True, max_length=8, db_index=True)
    votesmart_id = models.CharField(max_length=6, db_index=True)
    fec_id = models.CharField(max_length=10, db_index=True)
    govtrack_id = models.CharField(max_length=8, db_index=True)
    crp_id = models.CharField(max_length=10, db_index=True)
    twitter_id = models.CharField(max_length=24, null=True, blank=True)
    congresspedia_url = models.CharField(max_length=128, null=True, blank=True)
    youtube_url = models.CharField(max_length=128, null=True, blank=True)
    facebook_id = models.CharField(max_length=128, null=True, blank=True)
    official_rss = models.CharField(max_length=64, null=True, blank=True)
    senate_class = models.CharField(max_length=3, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    oc_email = models.EmailField(null=True, blank=True)

    class Meta:
        ordering = ('lastname',)

    def __unicode__(self):
        return unicode("%s %s" % (self.firstname, self.lastname))

    def city_state_zip(self):
        return "%s" % (settings.WASHINGTON_DC_ADDRESS)

    def full_name(self):
        return unicode("%s %s" % (self.firstname, self.lastname))

    def title_and_name(self):
        return unicode("%s. %s %s (%s %s)" % (
            self.title,self.firstname,self.lastname, self.state, self.district))

# Multiple offices for state legislators
class Office(models.Model):
    address = models.CharField(max_length=128, null=True, blank=True)
    type = models.CharField(max_length=24, null=True, blank=True)
    name = models.CharField(max_length=36, null=True, blank=True)
    phone = models.CharField(max_length=16, null=True, blank=True)
    fax = models.CharField(max_length=16, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __unicode__(self):
        return unicode("%s: %s" % (self.type, self.address))

class StateLegislator(models.Model):
    active = models.BooleanField()
    chamber = models.CharField(max_length=16)
    leg_id = models.CharField(max_length=16, unique=True, db_index=True)
    level = models.CharField(max_length=16)
    district = models.CharField(max_length=36, null=True, blank=True, db_index=True)
    email = models.EmailField(null=True, blank=True)
    first_name = models.CharField(max_length=36, null=True, blank=True)
    middle_name = models.CharField(max_length=36, null=True, blank=True)
    last_name = models.CharField(max_length=36, null=True, blank=True)
    full_name = models.CharField(max_length=48, null=True, blank=True)
    offices = models.ManyToManyField(Office)
    party = models.CharField(max_length=24, null=True, blank=True)
    photo_url = models.URLField(max_length=500, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    suffixes = models.CharField(max_length=24, null=True, blank=True)
    url = models.URLField(max_length=500, null=True, blank=True)
    votesmart_id = models.CharField(max_length=6, db_index=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    transparencydata_id = models.CharField(max_length=48, null=True, blank=True, db_index=True)
    all_ids = models.CharField(max_length=256, null=True, blank=True)
    country = models.CharField(max_length=2, null=True, blank=True)

    class Meta:
        ordering = ('last_name',)

    def __unicode__(self):
        return unicode("%s %s" % (self.first_name,self.last_name))

class DelegateSummary(models.Model):
    state = models.OneToOneField(State)
    allocation_pledged = models.IntegerField(default=0)
    allocation_unpledged = models.IntegerField(default=0)
    available_pledged = models.IntegerField(default=0)
    available_unpledged = models.IntegerField(default=0)
    sanders_pledged = models.IntegerField(default=0)
    sanders_unpledged = models.IntegerField(default=0)
    clinton_pledged = models.IntegerField(default=0)
    clinton_unpledged = models.IntegerField(default=0)

    class Meta:
        ordering = ('state__name',)
        verbose_name_plural = 'delegate summaries'

    def __unicode__(self):
        return unicode("%s" % (self.state.state))
