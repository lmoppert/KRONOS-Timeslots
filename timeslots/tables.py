from django.utils.translation import ugettext_lazy as _
import django_tables2 as tables

from timeslots.models import Job


class JobTable(tables.Table):
    slot_times = tables.Column(
            accessor='slot.times', 
            order_by=('slot.block.start'),
            verbose_name=_('Time')
            )
    number = tables.Column(verbose_name=_('Job'))
    slot_block_dock = tables.Column(
            accessor='slot.block.dock.name', 
            order_by=('slot.block.dock.name'),
            verbose_name=_('Dock')
            )
    slot_company = tables.Column(
            accessor='slot.company', 
            order_by=('slot.company.company'),
            verbose_name=_('Company')
            )
    description = tables.Column(verbose_name=_('Description'))

    class Meta:
        attrs = {'class': "table table-bordered table-striped"}
