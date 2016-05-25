import re
import pytz
import datetime
import logging
from django import template
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from adrestia.models import Candidate

log = logging.getLogger(__name__)

register = template.Library()

@register.assignment_tag()
def contains(value, arg):
  """
  Usage:
  {% if text|contains:"http://" %}
  This is a link.
  {% else %}
  Not a link.
  {% endif %}
  """

  return arg in value

@register.simple_tag
def title_and_name(obj, additional=False):
  """
  Usage:
  """
  return mark_safe(obj.title_and_name(additional=additional))

@register.simple_tag
def candidate_office(c):
  """
  Usage:
  """
  ret = []

  state = c.state
  level = c.level
  office = c.office
  district = c.district

  try:
      if level == 'Federal':
          ret.append(office)
          ret.append(district)
      elif level == 'State':
          if office in ('Governor', 'Lt. Governor', 'Secretary of State'):
              ret.append(office)
          else:
              ret.append(level)
              ret.append(office)
              ret.append(district)
      elif level in Candidate.LEVEL_LIST:
          ret.append(office)
          ret.append(district)
      if not ret:
          log.error('Candidate %s: %s, %s, %s, %s', c, state, level, office,
                  district)
          ret.append('Unknown')
  except:
      raise
      log.error('Unknown error')
      pass

  return format_html('{} {}', mark_safe(state), mark_safe(' '.join(ret)))

@register.simple_tag
def incumbent_or_opponent(c):
  """
  Usage:
  """
  ret = []
  today = datetime.date.today()
  today = pytz.timezone('UTC').localize(datetime.datetime.utcnow())
  try:
      raise
      if c.serving: ret.append('Incumbent')
      if c.running: ret.append('Running')
      if not ret:
          ret.append('Status Unknown')

      # passed
#      if today > c.state.primary_date and c.level in ('Federal', 'State'):
#          if today < c.state.general_date:
#              if c.primary_win == False: ret = ['Defeated']
#              elif c.primary_win == True: ret = ['Primary Winner']
#              elif c.primary_win == None: ret = ['Won or Lost?']
#          else:
#              if c.general_win == False: ret = ['Defeated']
#              elif c.general_win == True: ret = ['Winner']
#              elif c.general_win == None: ret = ['Won or Lost?']
  except:
      pass
#  if ((c.legislator and c.legislator.lastname in c.name) or
#      (c.state_legislator and c.state_legislator.last_name in c.name)):
#      #return 'Incumbent: %s, %s' % (c.legislator, c.state_legislator)
#      ret.add('Incumbent')

  return format_html('{}', mark_safe(', '.join(ret)))

@register.simple_tag
def party(c):
  """
  Usage:
  """
  if c.party:
      return mark_safe(Candidate.PARTY_DICT[c.party])
  else:
      return mark_safe('Unknown')

@register.simple_tag
def election_info(c):
    """
    Usage:
    """
    ret = []
    today = pytz.timezone('UTC').localize(datetime.datetime.utcnow())
    leadup = datetime.timedelta(days=14)
    fmt = '%a, %b %d %Y'

    def leadup_snippet(state, election):
        if election == 'Primary':
            date = state.primary_date
        elif election == 'General':
            date = state.general_date
        election_end = state.election_end

        snippet = u'<br/><span class="text-danger election">%s: %s' % (
              election,
              date.strftime(fmt),
        )
        if date <= today < election_end:
            snippet += '<br/>Polls open, go vote!</span>'
        else:
            snippet += '<br/>%s</span>' % naturaltime(date)

        return snippet.encode('utf-8')

    try:
        if c.serving: ret.append('Incumbent')
        if c.running: ret.append('Candidate')

        # estimate polls closing time as opening + 12 hours
        c.state.election_end = c.state.primary_date+datetime.timedelta(hours=12)
        # before primary or general election
        if today <= c.state.election_end:
            if c.state.primary_date - leadup < today:
                ret.append(leadup_snippet(c.state, 'Primary'))
        elif today <= c.state.general_date:
            if c.state.general_date - leadup < today:
                ret.append(leadup_snippet(c.state, 'General'))
            if c.primary_win == True:
                ret.append('<br/>Primary winner <i class="fa fa-smile-o text-success smiley"></i>')
            elif c.primary_win == False:
                ret.append('<br/>Defeated <i class="fa fa-frown-o text-danger smiley"></i>')
            elif c.primary_win == None and c.level in ('Federal', 'State'):
                ret.append('<br/>Won or Lost <i class="fa fa-question"></i>')
        else:
            if c.general_win == True:
                ret.append('<i class="fa fa-smile-o text-success smiley"></i>')
            elif c.general_win == False:
                ret.append('<i class="fa fa-frown-o text-danger smiley"></i>')
            elif c.general_win == None and c.level in ('Federal', 'State'):
                ret.append('<br/>Won or Lost <i class="fa fa-question"></i>')
  
    except Exception, e:
        log.error('Tag error: %s', e)
  
    return format_html('{}', mark_safe(' '.join(ret)))

@register.filter(needs_autoescape=True)
def unused(value, autoescape=True):
  """
  Usage: convert newlines to <br/>
  """
  try:
      return re.sub('\n', '<br/>', value.strip())
  except:
      print 'error'
      return value
