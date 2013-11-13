"""Table definitions for the Timeslots application."""

from django.utils.translation import ugettext_lazy as _
import django_tables2 as tables
from django_tables2.utils import A


class JobTable(tables.Table):

    """Display all jobs for a day in a table."""

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
        accessor='slot.times_flagged',
        order_by=('slot.block.start', 'slot.timeslot', 'slot.line'),
        verbose_name=_('Time')
    )
    slot_block_dock = tables.Column(
        accessor='slot.block.dock.name',
        order_by=('slot.block.dock.name'),
        verbose_name=_('Dock')
    )
    payload = tables.Column(verbose_name=_('Payload'))
    description = tables.Column(verbose_name=_('Description'))

    class Meta:

        """Meta information for the job table."""

        sequence = ('number', 'slot_times', 'slot_block_dock', 'payload',
                    'description')


class StationJobTable(JobTable):

    """Display all jobs of a station in a table."""

    slot_company = tables.Column(
        accessor='slot.company',
        order_by=('slot.company.company'),
        verbose_name=_('Company')
    )

    class Meta:

        """Meta information for the station job table."""

        attrs = {'class': "table table-bordered table-striped"}
        empty_text = _('No open jobs')
        order_by = ('number',)
        sequence = ('number', 'slot_company', 'slot_times', 'slot_block_dock',
                    'payload', 'description')


class UserJobTable(JobTable):

    """Display all jobs of a user in a table."""

    slot_date = tables.Column(
        accessor='slot.date',
        order_by=('slot.date'),
        verbose_name=_('Date')
    )
    station = tables.Column(
        accessor='slot.block.dock.station',
        order_by=('slot.block.dock.station'),
        verbose_name=_('Station')
    )

    class Meta:

        """Meta information for the user job table."""

        attrs = {'class': "table table-bordered table-striped"}
        empty_text = _('No open jobs')
        sequence = ('number', 'slot_date', 'slot_times', 'slot_block_dock',
                    'payload', 'description', 'station')


class UserTable(tables.Table):

    """Display all users in a table."""

    id = tables.Column(accessor='id')
    username = tables.Column(accessor='username')
    company = tables.Column(accessor='userprofile.company')
    firstname = tables.Column(accessor='first_name')
    lastname = tables.Column(accessor='last_name')
    #street = tables.Column(accessor='userprofile.street')
    #ZIP = tables.Column(accessor='userprofile.ZIP')
    #town = tables.Column(accessor='userprofile.town')
    #country = tables.Column(accessor='userprofile.country')
    email = tables.Column(accessor='email')
    #phone = tables.Column(accessor='userprofile.phone')
    language = tables.Column(accessor='userprofile.language')
    group = tables.TemplateColumn(template_name='timeslots/column_group.html')
    stations = tables.TemplateColumn(
        template_name='timeslots/column_stations.html')
    is_staff = tables.Column(accessor='is_staff')

    class Meta:

        """Meta information for the user table."""

        attrs = {'class': "table table-bordered table-striped"}
