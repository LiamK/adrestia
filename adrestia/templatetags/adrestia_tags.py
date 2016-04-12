from django import template

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
  if ((c.legislator and c.legislator.lastname in c.name) or
      (c.state_legislator and c.state_legislator.last_name in c.name)):
      #return 'Incumbent: %s, %s' % (c.legislator, c.state_legislator)
      return 'Incumbent'
  elif c.legislator:
      return "<strong>L %s</strong>" % c.legislator.lastname
      return '{} {}'.format(c.legislator.firstname, c.legislator.lastname)
  elif c.state_legislator:
      return "<strong>S %s</strong>" % c.state_legislator.full_name
      return c.state_legislator.full_name
  return ''


