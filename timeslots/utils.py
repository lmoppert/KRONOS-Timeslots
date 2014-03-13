"""Definition of some helper functions to the Timeslots application."""

from django.db.models import Count
from django.utils.timezone import now
from django.utils.decorators import method_decorator

from datetime import datetime, timedelta
from timeslots.models import Slot, Logging


# Helper functions
def log_msg(request, message, object="<NONE>"):
    """Create an log entry for the submitted task."""
    logentry = Logging.objects.create(
        user=request.user,
        host=request.META.get('REMOTE_ADDR'),
        task=message.format(user=request.user, object=object)
    )
    logentry.save()


def daterange(start, end):
    """Calculate the renge between two given dates."""
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    for n in range(int((end_date - start_date).days + 1)):
        yield start_date + timedelta(n)


def delete_slot_garbage(request):
    """Garbage Collector for uncompleted slot reservations."""
    # annotate creates a filterable value (properties not available in filters)
    slots = Slot.objects.filter(is_blocked=False).annotate(
        num_jobs=Count('job')).filter(num_jobs__exact=0)
    for slot in slots:
        if now() - slot.created > timedelta(minutes=5):
            msg = "The garbage collector has deleted slot {object} (%s)"
            log_msg(request, msg % slot.times, slot)
            slot.delete()


def cbv_decorator(decorator):
    """Return a decorator for class based viewes."""
    def _decorator(cls):
        cls.dispatch = method_decorator(decorator)(cls.dispatch)
        return cls
    return _decorator
