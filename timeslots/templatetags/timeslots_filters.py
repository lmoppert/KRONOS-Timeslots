from django.utils.encoding import force_unicode
from django.utils.translation import get_language
from django.template import Library
from babel.dates import format_date
from datetime import date
import locale

register = Library()


@register.filter
def get_range(value):
    """
    Returns a list containing range made from given value.

    Usage (in template)::

        <ul>{% for i in 3|get_range %}
                <li>{{ i }}. Do something</li>
        {% endfor %}</ul>

    Results in the following HTML code::

        <ul>
                <li>1. Do something</li>
                <li>2. Do something</li>
                <li>3. Do something</li>
        </ul>

    Instead of 3 one may use a variable set in the views
    """
    return [v + 1 for v in range(value)]


@register.filter
def make_date(curr_date):
    """
    The date is converted from YYYY-MM-DD to a real date representation
    """
    date_obj = date(int(curr_date[:4]), int(curr_date[5:7]),
                    int(curr_date[8:10]))
    if get_language() == "de":
        date_str = format_date(date_obj, format='full', locale='de_DE')
    else:
        date_str = format_date(date_obj, format='full', locale='en')

    return date_str


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
