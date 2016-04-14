import re
import datetime
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import format_html

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
def incumbent_or_opponent(c):
  """
  Usage:
  """
  ret = []
  today = datetime.date.today()
  leadup = datetime.timedelta(days=14)
  try:
      if c.serving: ret.append('Incumbent')
      if c.running: ret.append('Running')
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
              ret = '<span class="text-success election">Primary: %s</span>' % c.state.primary_date.strftime(fmt);
      elif today <= c.state.general_date:
          if c.state.general_date - leadup < today:
              ret = '<span class="text-success election">General: %s</span>' % c.state.general_date.strftime(fmt);
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
      print 'Error in filter', e

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
