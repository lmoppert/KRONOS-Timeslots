from django.db.models import Count
from django.utils.timezone import now
from django.utils.decorators import method_decorator

from datetime import datetime, timedelta
from timeslots.models import *

# Helper functions
def log_task(request, message):
    logentry = Logging.objects.create(
            user=request.user, 
            host=request.META.get('REMOTE_ADDR'), 
            task = message)
    logentry.save()

def daterange(start, end):
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    for n in range(int ((end_date - start_date).days + 1)):
        yield start_date + timedelta(n)

def delete_slot_garbage(request):
    # annotate creates a filterable value (properties cannot be accessed in filters)
    slots = Slot.objects.annotate(num_jobs=Count('job')).filter(num_jobs__exact=0)
    for slot in slots:
        if not slot.is_blocked and now() - slot.created > timedelta(minutes=5):
            log_task(request, "The garbage collector has deleted slot %s" % slot)
            slot.delete()

def cbv_decorator(decorator):
    def _decorator(cls):
        cls.dispatch = method_decorator(decorator)(cls.dispatch)
        return cls
    return _decorator

