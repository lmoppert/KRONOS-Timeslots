from django.utils.encoding import force_unicode
from django.template import Library
from datetime import date
import locale

register = Library()

@register.filter
def get_range( value ):
  """
    Filter - returns a list containing range made from given value
    Usage (in template):

    <ul>{% for i in 3|get_range %}
      <li>{{ i }}. Do something</li>
    {% endfor %}</ul>

    Results with the HTML:
    <ul>
      <li>1. Do something</li>
      <li>2. Do something</li>
      <li>3. Do something</li>
    </ul>

    Instead of 3 one may use the variable set in the views
  """
  return [v + 1 for v in range(value)]

@register.filter
def nice_date(curr_date, arg="long"):
    """
      The date is converted from YYYY-MM-DD to the german standard:

      DD.MM.YYYY
    """
    locale.setlocale(locale.LC_TIME, "de_DE.utf8")
    nice_date = date(int(curr_date[:4]), int(curr_date[5:7]), int(curr_date[8:10]))
    if arg == "long":
        return nice_date.strftime("%A, %d. %B %Y")
    else:
        return nice_date.strftime("%a, %d.%m.")
    
@register.filter
def in_group(user, groups):
    """
      Returns a boolean if the user is in the given group, or comma-separated
      list of groups.

      Usage::
          {% if user|in_group:"Friends" %}
          ...
          {% endif %}

      or::
          {% if user|in_group:"Friends,Enemies" %}
          ...
          {% endif %}
    """
    group_list = force_unicode(groups).split(',')
    return bool(user.groups.filter(name__in=group_list).values('name'))
