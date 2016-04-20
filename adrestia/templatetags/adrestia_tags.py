import re
import datetime
import logging
from django import template
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
          ret.append(district)
      elif level == 'Local':
          ret.append(office)
          ret.append(district)
      elif level == 'State':
          if office in ('Governor', 'Lt. Governor', 'Secretary of State'):
              ret.append(office)
          else:
              ret.append(level)
              ret.append(office)
              ret.append(district)
      if not ret:
          ret.append('Unknown')
  except:
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
  try:
      if c.serving: ret.append('Incumbent')
      if c.running: ret.append('Running')
      if not ret:
          ret.append('Unknown')
      # passed
      if today > c.state.primary_date:
          if not c.winner: ret = ['Defeated']
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
  return mark_safe(Candidate.PARTY_DICT[c.party])

@register.simple_tag
def election_info(c):
  """
  Usage:
  """
  ret = ''
  today = datetime.date.today()
  leadup = datetime.timedelta(days=14)
  fmt = '%a, %b %d %Y'
  try:
      # leadup
      if today <= c.state.primary_date:
          if c.state.primary_date - leadup < today:
              ret = '<br/><span class="text-success election">Primary: %s</span>' % c.state.primary_date.strftime(fmt);
      elif today <= c.state.general_date:
          if c.state.general_date - leadup < today:
              ret = '<br/><span class="text-success election">General: %s</span>' % c.state.general_date.strftime(fmt);
      # passed
      if today > c.state.primary_date:
          if today < c.state.general_date:
              if c.winner:
                  ret = '<i class="fa fa-meh-o text-warning smiley"></i>'
              else:
                  ret = '<i class="fa fa-frown-o text-danger smiley"></i>'
          else:
              if c.winner:
                  ret = '<i class="fa fa-smile-o text-success smiley"></i>'
              else:
                  ret = '<i class="fa fa-frown-o text-danger smiley"></i>'
  except Exception, e:
      log.error('Tag error: %s', e)

  #ret_str = ', '.join(ret)
  return format_html('{}', mark_safe(ret))

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
