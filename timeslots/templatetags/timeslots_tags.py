from django import template
from django.utils.translation import ugettext_lazy as _

register = template.Library()


#class SlotProgress(template.Node):
#    def __init__(self, progress, nodelist_true, nodelist_false):
#        self.slot = template.Variable(slot)
#
#    def render(self, context):
#        try:
#            slot = self.slot.resolve(context)
#        except template.VariableDoesNotExist:
#            return ''
#        if slot 
#
#@register.tag(name='show_progress')
#def do_show_progress(parser, token):
#    """The ``{% slot %}`` tag displays a button to change the progress of a slot and 
#    additionally a colorized progress bar, that represents the current progress status
#    """
#    try:
#        tag_name, progress = token.split_contents()
#    except ValueError:
#        raise template.TemplateSyntaxError('%s requires a Progress as argument' % token.contents.split()[0])
#    return SlotProgress(slot)

@register.inclusion_tag('timeslots/progress.html')
def show_progress(slot, user):
    """
    Displays a colorized progress bar representing the current status of the corresponding SLOT.
    The bar is linked to a javascript fuction that increases the current status by one step.

    Usage (in template)::

        {% show_progress SLOT %}

    The tag uses the template ``timeslots/progress.html`` to render the progress bar
    """
    progress = slot.progress
    if progress == 0:
        div_title = _("Slot has been booked")
        div_class = "progress"
        div_style = "width: 0%"
    elif progress == 1:
        div_title = _("Carrier is checking in")
        div_class = "progress progress-danger"
        div_style = "width: 25%"
    elif progress == 2:
        div_title = _("Carrier is beeing loaded")
        div_class = "progress progress-warning"
        div_style = "width: 50%"
    elif progress == 3:
        div_title = _("Carrier is checking out")
        div_class = "progress progress-success"
        div_style = "width: 75%"
    else:
        div_title = _("Slot has been processed")
        div_class = "progress"
        div_style = "width: 100%"
    return {'div_title': div_title, 'div_class': div_class, 'div_style': div_style, 'progress': progress, 
            'slot_id': slot.id, 'station_id': slot.block.dock.station.id, 'date': slot.date}
