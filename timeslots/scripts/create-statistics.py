from timeslots import models


slots = models.Slot.objects.filter(is_blocked=False)
stations = models.Station.objects.exclude(pk__in=(10, 15, 17))
slotcount = {}
for station in stations:
    station_slots = slots.filter(block__dock__station=station)
    year_list = []
    for year in (2016, 2017, 2018):
        year_slots = station_slots.filter(date__year=year)
        month_list = []
        for month in range(1, 13):
            month_list.append(year_slots.filter(date__month=month).count())
        year_list.append((year, year_slots.count(), month_list))
    slotcount[station] = (station_slots.count(), year_list)
print(slotcount)
