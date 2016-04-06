
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import State, DNCGroup, PresidentialCandidate

class StateModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class GroupModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class DelegateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DelegateForm, self).__init__(*args, **kwargs)

        self.fields['state'].empty_label = 'Select a State'
        self.fields['group'].empty_label = 'DNC Group'
        self.fields['candidate'].empty_label = 'Pledged to...'

        self.helper = FormHelper()
        self.helper.form_id = 'id-delegate-form'
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.form_method = 'post'
        self.helper.form_action = 'delegate_list'

        self.helper.add_input(Submit('submit', 'Submit'))

    state = StateModelChoiceField(label='', queryset=State.objects.all().order_by('name'), required=False)
    group = GroupModelChoiceField(label='', queryset=DNCGroup.objects.all().order_by('name'), required=False)
    candidate = forms.ModelChoiceField(label='',
        queryset=PresidentialCandidate.objects.all().order_by('name'), required=False)
