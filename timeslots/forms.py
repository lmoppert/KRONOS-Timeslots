from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.utils.translation import ugettext as _
from django import forms
from timeslots.models import Slot, Job, Station


class BlockSlotForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BlockSlotForm, self).__init__(*args, **kwargs)
        self.station = kwargs.pop('station', None)

    class Meta:
        model = Slot
        exclude = ('company',)

    def _get_times(self):
        slot_times = () 
        for d in self.station.dock_set.all():
            for b in d.block_set.all():
                slot_times.append((b.dock, b.start_times))
        return slot_times

    #start = forms.DateField()
    #end = forms.DateField()
    #slots = forms.MultipleChoiceField(choices = _get_times())


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

