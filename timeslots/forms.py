from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.utils.translation import ugettext as _
from django import forms
from timeslots.models import *
from datetime import date


class BlockSlotForm(forms.Form):
    block = forms.ModelChoiceField(queryset=Block.objects.none())
    start = forms.DateField(initial=date.today)
    end = forms.DateField(initial=date.today)
    slots = forms.MultipleChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        stations = kwargs.pop('stations', None)
        timeslots = kwargs.pop('timeslots', None)
        super(BlockSlotForm, self).__init__(*args, **kwargs)
        if stations:
            self.fields["block"].queryset = Block.objects.filter(dock__station__in=stations)
        if timeslots:
            self.fields["slots"].choices = timeslots


class RequireOneFormSet(BaseInlineFormSet):
    """Require at least one form in the formset to be completed."""
    def clean(self):
        super(RequireOneFormSet, self).clean()
        for error in self.errors:
            if error:
                return
        completed = 0
        for cleaned_data in self.cleaned_data:
            # form has data and we aren't deleting it.
            if cleaned_data and not cleaned_data.get('DELETE', False):
                completed += 1

        if completed < 1:
            raise forms.ValidationError(_("At least one %s is required.") %
                self.model._meta.verbose_name)

JobFormSet = inlineformset_factory(Slot, Job, extra=1, formset=RequireOneFormSet)

