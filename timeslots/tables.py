from django.utils.translation import ugettext_lazy as _
import django_tables2 as tables
from django_tables2.utils import A

from timeslots.models import Job


class JobTable(tables.Table):
    number = tables.LinkColumn(
            'timeslots_slot_detail',
            kwargs={'block_id': A('slot.block.id'),
                    'timeslot': A('slot.timeslot'),
                    'line': A('slot.line'),
                    'date': A('slot.date_string')
                    },
            verbose_name=_('Job')
            )
    slot_times = tables.Column(
            accessor='slot.times', 
            order_by=('slot.block.start', 'slot.timeslot', 'slot.line'),
            verbose_name=_('Time')
            )
    slot_block_dock = tables.Column(
            accessor='slot.block.dock.name', 
            order_by=('slot.block.dock.name'),
            verbose_name=_('Dock')
            )
    description = tables.Column(verbose_name=_('Description'))


class StationJobTable(JobTable):
    slot_company = tables.Column(
            accessor='slot.company', 
            order_by=('slot.company.company'),
            verbose_name=_('Company')
            )

    class Meta:
        attrs = {'class': "table table-bordered table-striped"}
        empty_text = _('No open jobs')
        sequence = ('number', 'slot_company', 'slot_times', 'slot_block_dock', 'description')


class UserJobTable(JobTable):
    slot_date = tables.Column(
            accessor='slot.date', 
            order_by=('slot.date'),
            verbose_name=_('Date')
            )

    class Meta:
        attrs = {'class': "table table-bordered table-striped"}
        empty_text = _('No open jobs')
        sequence = ('number', 'slot_date', 'slot_times', 'slot_block_dock', 'description')

