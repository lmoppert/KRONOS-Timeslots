from django.forms.models import inlineformset_factory
from django.forms import ModelForm
from timeslots.models import Slot, Job

JobFormSet = inlineformset_factory(Slot, Job, extra=1)
