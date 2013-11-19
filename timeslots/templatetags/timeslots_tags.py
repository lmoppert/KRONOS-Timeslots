from django import template
from django.utils.translation import ugettext_lazy as _

register = template.Library()


@register.inclusion_tag('timeslots/progress.html')
def show_progress(slot, user):
    """
    Displays a colorized progress bar representing the current status of the
    corresponding SLOT. The bar is linked to a javascript fuction that
    increases the current status by one step.

    Usage (in template)::

        {% show_progress SLOT %}

    The tag uses the template ``timeslots/progress.html`` to render the
    progress bar
    """
    progress = slot.progress
    if progress == 1:
        div_title = _("Carrier is checking in")
        div_class = "progress progress-danger"
        div_style = "width: 33%"
    elif progress == 2:
        div_title = _("Carrier is beeing loaded")
        div_class = "progress progress-warning"
        div_style = "width: 66%"
    elif progress == 3:
        div_title = _("Carrier has checked out")
        div_class = "progress progress-success"
        div_style = "width: 100%"
    else:
        div_title = _("Slot has been booked")
        div_class = "progress"
        div_style = "width: 0%"
    return {'user': user, 'div_title': div_title, 'div_class': div_class,
            'div_style': div_style, 'progress': progress, 'slot_id': slot.id,
            'station_id': slot.block.dock.station.id, 'date': slot.date}
