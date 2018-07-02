from timeslots.models import Slot, Block, UserProfile
from datetime import date, timedelta

block = Block.objects.get(pk=52)
company = UserProfile.objects.get(pk=1)
saturday = date(2018, 1, 6)
sat_list = [saturday + timedelta(days=x) for x in range(0 ,358, 7)]
for sat in sat_list:
    # Saturdays from 13.30 h till end
    dstr = sat.strftime('%Y-%m-%d')
    for ts in range(19,33):
        s = Slot(block=block, company=company, date=dstr, timeslot=ts,
                is_blocked=1, line=1)
        s.save()

    # Sundays till 21.45 h
    dstr = (sat + timedelta(days=1)).strftime('%Y-%m-%d')
    for ts in range(1,30):
        s = Slot(block=block, company=company, date=dstr, timeslot=ts,
                is_blocked=1, line=1)
        s.save()
