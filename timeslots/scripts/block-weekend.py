from timeslots.models import Slot, Block, UserProfile
from datetime import date, timedelta

block = Block.objects.get(pk=57)                # TODO Choose block id
saturday = date(2018, 7, 7)                     # TODO Add starting date
company = UserProfile.objects.get(pk=1)
sat_list = [saturday + timedelta(days=x) for x in range(0, 175, 7)]
for sat in sat_list:
    # Saturdays
    dstr = sat.strftime('%Y-%m-%d')
    for ts in range(12,21):                     # TODO Choose slots to block
        s = Slot(block=block, company=company, date=dstr, timeslot=ts,
                is_blocked=1, line=1)           # TODO Choose line to block
        s.save()

    # Sundays
    dstr = (sat + timedelta(days=1)).strftime('%Y-%m-%d')
    for ts in range(1,21):                      # TODO Choose slots to block
        s = Slot(block=block, company=company, date=dstr, timeslot=ts,
                is_blocked=1, line=1)           # TODO Choose line to block
        s.save()

# ** HISTORY **
#
# KRONOS Nordenham - Truck
#     saturday = date(2018, 1, 6)
#     sat_list = ... range(0, 358, 7)
#     Sat: range(19, 33)
#     Sun: range(1, 30)
#
# KRONOS Leverkusen - ecochem F19
#     saturday = date(2018, 7, 7)
#     sat_list = ... range(0, 176, 7)
#     Sat: range(12, 21)
#     Sun: range(1, 21)
