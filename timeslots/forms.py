from datetime import date

from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import *
from crispy_forms.layout import *
from timeslots.models import *


class BlockSlotForm(forms.Form):
    block = forms.ModelChoiceField(
                label=_("Choose block"),
                queryset=Block.objects.none(),
            )
    start = forms.DateField(
                label=_("Block from"),
            )
    end = forms.DateField(
                label=_("Block until"),
            )
    slots = forms.MultipleChoiceField(
                label=_("Slots"),
                choices=[],
            )

    def __init__(self, *args, **kwargs):
        stations = kwargs.pop('stations', None)
        timeslots = kwargs.pop('timeslots', None)
        self.helper = FormHelper()
        self.helper.layout = Layout (
                Div(
                    Field('block'), 
                    css_class="span12"
                ),
                Div(
                    AppendedText('start', '<a href="#"><i class="icon-calendar"></i></a>', css_class="date_picker_field"),
                    AppendedText('end', '<a href="#"><i class="icon-calendar"></i></a>', css_class="date_picker_field"), 
                    css_class="span3"
                ), 
                Div(
                    Field('slots', size="12"), 
                    css_class="span4"
                ),
                Div(
                    Submit('blockSlots', _("Block selected slots"), css_class="btn-danger"),
                    Submit('releaseSlots', _("Release selected slots"), css_class="btn-success"),
                    css_class="span12"
                )
            )
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
            raise forms.ValidationError(_("At least one %(model)s is required.") % {'model': self.model._meta.verbose_name})

JobFormSet = inlineformset_factory(Slot, Job, extra=1, formset=RequireOneFormSet)
SingleJobForm = inlineformset_factory(Slot, Job, extra=1, max_num=1, formset=RequireOneFormSet)
