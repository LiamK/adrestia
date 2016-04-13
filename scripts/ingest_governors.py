#!/usr/bin/python
import sys
import urllib2
from bs4 import BeautifulSoup
from bs4.diagnose import diagnose
import csv
import re

from adrestia.models import *

url = 'http://www.nga.org/cms/home/governors/staff-directories--contact-infor/col2-content/governors-office-addresses-and-w.default.html'

def run():
    response = urllib2.urlopen(url)
    html = response.read().decode('utf-8')

    # Parse the Wikipedia page
    soup = BeautifulSoup(html, 'html.parser')

    # Get the table with the data
    table = soup.find('table')

    # Get table rows, delete the first one
    rows = table.find_all('p')

    # Write the first row
    #writer = csv.writer(sys.stdout)
    #writer.writerow([
    #        'delegate',
    #        'delegate_url',
    #        'state',
    #        'group',
    #        'group_sup_url',
    #        'group_sup_text',
    #        'candidate',
    #        'candidate_sup_url',
    #        'candidate_sup_text',
    #    ])

    # Write out each row
    for r in rows:
        state_element = r.strong
        state = state_element.text.strip()
        website = ''
        website_text = ''
        address = []
        phone = ''
        fax = ''

        try:
            last_name = re.search(r'Office of Governor ([^\n]+)', r.text).group(1)
            last_name = last_name.split(' ')[-1:][0]
            delegate = Delegate.objects.get(group__name='Governor',
                    state__name=state, name__icontains=last_name)
        except Delegate.DoesNotExist:
            continue

        try:
            website_element = r.a
            if website_element:
                website_text = website_element.text
                website = website_element.get('href')
        except:
            raise
            website = ''

        try:
            clipped = r.text.replace(state, '')
            clipped = clipped.replace(website_text, '')
            lines = clipped.split('\n')
            for line in lines:
                line = line.strip()
                if 'Phone'in line:
                    phone = line.replace('Phone: ', '')
                    phone = phone.replace(' ', '')
                    phone = phone.replace('/', '-')
                elif 'Fax:'in line:
                    fax = line.replace('Fax: ', '')
                    fax = fax.replace(' ', '')
                    fax = fax.replace('/', '-')
                else:
                    if line != '':
                        address.append(line)
            print '\n'.join(address) 
            print phone
            print fax
            print website
            print
        except:
            raise

        delegate.phone = phone
        delegate.fax = fax
        delegate.website_url = website
        delegate.address = '\n'.join(address) 
        delegate.save()
