
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Submit
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

        self.fields['state'].empty_label = 'Any State'
        self.fields['group'].empty_label = 'Any Group'
        self.fields['candidate'].empty_label = 'Any Candidate'

        self.helper = FormHelper()
        self.helper.form_id = 'id-delegate-form'
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'adrestia/bootstrap3/layout/inline_field.html'
        self.helper.form_method = 'post'
        self.helper.form_action = 'delegate_list'

        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
                Field('state', template=self.helper.field_template),
                Field('group', template=self.helper.field_template),
                Field('candidate', template=self.helper.field_template),
                Field('has_opponents', css_class='checkbox-primary',
                    template=self.helper.field_template),
                )

        # Field('has_opponents', css_class="whatever")

    state = StateModelChoiceField(label='',
            to_field_name='state', queryset=State.objects.all().order_by('name'), required=False)
    group = GroupModelChoiceField(label='',
            to_field_name='abbr', queryset=DNCGroup.objects.all().order_by('name'), required=False)
    candidate = forms.ModelChoiceField(label='',
            to_field_name='name', queryset=PresidentialCandidate.objects.all().order_by('name'), required=False)
    has_opponents = forms.BooleanField(label='Opponent?', required=False)
