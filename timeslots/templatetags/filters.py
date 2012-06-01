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
def nice_date( curr_date ):
    """
      The date is converted from YYYY-MM-DD to the german standard:

      DD.MM.YYYY
    """
    locale.setlocale(locale.LC_TIME, "de_DE.utf8")
    nice_date = date(int(curr_date[:4]), int(curr_date[6:7]), int(curr_date[9:10]))
    return nice_date.strftime("%A, %d. %B %Y")
    
