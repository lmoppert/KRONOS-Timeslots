from django.forms.models import inlineformset_factory
from timeslots.models import Slot, Job

JobFormSet = inlineformset_factory(Slot, Job)
