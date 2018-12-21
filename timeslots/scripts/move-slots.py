from timeslots.models import Slot
from datetime import date


for block in [7, 9]:
    for slot in Slot.objects.filter(block=block, timeslot__lt=3, date__gt=date(2018, 1, 1)).order_by('-timeslot'):
        slot.timeslot += 1
        try:
            slot.save()
        except:
            pass
