from django import template

register = template.Library()


class SlotProgress(progress, nodelist_true, nodelist_false):
    def __init__(self, progress, nodelist_true, nodelist_false):
        self.progress = template.Variable(progress)
        self.nodelist_true = template.Variable(nodelist_true)
        self.nodelist_false = template.Variable(nodelist_false)

    def render(self, context):
        try:
            progress = self.progress.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        if 

@register.tag(name='slot')
def do_slot(parser, token):
    """The ``{% slot %}`` tag displays a button to change the progress of a slot and 
    additionally a colorized progress bar, that represents the current progress status
    """
    try:
        tag_name, progress = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
                '%s requires a Progress as argument' % token.contents.split()[0])
    nodelist_true = parser.parse('endslot')
    token = parser.next_token()
    nodelist_false = template.NodeList()
    return SlotProgress(progress)
