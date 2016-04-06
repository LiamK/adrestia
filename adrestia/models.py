from __future__ import unicode_literals

import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.utils.html import format_html
from django.utils.text import slugify

log = logging.getLogger(__name__)

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

    class Meta:
        ordering = ('state',)

    def __unicode__(self):
        return unicode(self.state)

class DNCGroup(models.Model):
    abbr = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=36, null=True)

    class Meta:
        ordering = ('abbr',)

    def __unicode__(self):
        return unicode(self.name)

class PresidentialCandidate(models.Model):
    name = models.CharField(max_length=36, unique=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return unicode(self.name)

class Candidate(models.Model):
    name = models.CharField(max_length=36)
    state = models.ForeignKey(State, null=True)
    level = models.CharField(max_length=12, null=True)
    office = models.CharField(max_length=24, null=True)
    district = models.CharField(max_length=36, null=True, blank=True)
    status = models.CharField(max_length=12, null=True)
    profile_url = models.URLField(max_length=500, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    primary_date = models.DateField(null=True, blank=True)
    legislator = models.ForeignKey('Legislator', to_field='bioguide_id',
            null=True, blank=True)
    state_legislator = models.ForeignKey('StateLegislator', to_field='leg_id',
            null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return unicode(self.name)


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

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
            return unicode("%s" % (self.name))

    def opponents(self):
        if self.legislator:
            qs = Candidate.objects.filter(state=self.state, district=self.legislator.district)
            qs = qs.exclude(name__contains=self.legislator.lastname)
            return qs
        elif self.state_legislator:
            qs = Candidate.objects.filter(state=self.state, district=self.state_legislator.district)
            qs = qs.exclude(name__contains=self.state_legislator.last_name)
            return qs
        else:
            return None

    def title_and_name(self):
        if self.legislator:
            return unicode("%s. %s (%s %s)" % (
                self.group.abbr, self.name, self.state, self.legislator.district))
        elif self.state_legislator:
            return unicode("%s. %s (%s %s)" % (
                self.group.abbr, self.name, self.state, self.state_legislator.district))
        else:
            return unicode("%s %s (%s)" % (self.group.abbr, self.name, self.state))

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
    oc_email = models.CharField(max_length=128, null=True, blank=True)

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
    email = models.CharField(max_length=128, null=True, blank=True)

    def __unicode__(self):
        return unicode("%s: %s" % (self.type, self.address))

class StateLegislator(models.Model):
    active = models.BooleanField()
    chamber = models.CharField(max_length=16)
    leg_id = models.CharField(max_length=16, unique=True, db_index=True)
    level = models.CharField(max_length=16)
    district = models.CharField(max_length=36, null=True, blank=True, db_index=True)
    email = models.CharField(max_length=128, null=True, blank=True)
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

