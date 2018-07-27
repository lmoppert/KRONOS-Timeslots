from timeslots.models import Slot


def run():
    for slot in Slot.objects.filter(date__year__lt=2018):
        for job in slot.job_set.all():
            job.delete()
        slot.delete()
