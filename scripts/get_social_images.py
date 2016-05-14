#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import imghdr

import logging
import sys
import pprint
import urllib2
from bs4 import BeautifulSoup
from bs4.diagnose import diagnose
import csv
import re

from django.core.files.temp import NamedTemporaryFile

from django.db.utils import IntegrityError
from django.db.models import Q

from adrestia.models import *

log = logging.getLogger(__name__)
log.info('Begin getting candidate images from social media')

def run():
    candidates = Candidate.objects.filter(
            (Q(twitter_id__isnull=False) |
             Q(facebook_id__isnull=False)) &
            (Q(image__isnull=True) |
             Q(image=''))
            )
    log.info('Processing %d candidates', candidates.count())

    for candidate in candidates:
        log.info(candidate.name)
        url = None
        if candidate.twitter_id:
            try:
                response = urllib2.urlopen('https://twitter.com/%s' % candidate.twitter_id)
                html = response.read().decode('utf-8')
                soup = BeautifulSoup(html, 'html.parser')
                avatar = soup.find('a', class_='ProfileAvatar-container')
                url = avatar['data-resolved-url-large']
                if url:
                    print 'Twitter:', url
                    process_image_url(candidate, url)
                continue
            except Exception, e:
                log.error(e)

        if candidate.facebook_id:
            try:
                response = urllib2.urlopen('https://facebook.com/%s' % candidate.facebook_id)
                html = response.read().decode('utf-8')
                soup = BeautifulSoup(html, 'html.parser')
                profile = soup.find('img', class_='profilePic')
                url = profile['src']
                if url:
                    print 'Facebook:', url
                    process_image_url(candidate, url)
            except Exception, e:
                log.error(e)

def process_image_url(candidate, url):
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
        #assert imghdr.what(image_file.name)
    except requests.exceptions.RequestException, e:
        log.error('%s', e)
        return
    except AssertionError:
        log.error('Not an image file: %s, %s', filename, url)
        return

    candidate.image.save(filename, File(image_file))
