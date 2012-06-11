from django import forms
from timeslots.models import Slot

class SlotForm(forms.ModelForm):
    class Meta:
        model = Slot
        exclude = ('is_blocked')
