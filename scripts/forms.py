from django.forms import ModelForm, HiddenInput, IntegerField, Textarea
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, Field 
from .models import InterestedPerson, Script, Step
from studies.models import Replica
from django.forms import ValidationError

class InterestedPersonForm(ModelForm):
    class Meta:
        model = InterestedPerson
        fields = ['email', 'contactme',]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = "E-mail:"
        self.fields['contactme'].label = "Check this box if you agree to be invited to participate in other research related to technologies applied to promote healthy ageing."

        self.helper = FormHelper()
        self.helper.form_id = 'id-thanksform'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'thanks'

        self.helper.layout = Layout(
            Row(
                Column('email', css_class='form-group col-md-8 mb-3 disabled'),
                css_class='form-row'
            ),
            Row(
                Column('contactme', css_class='form-group col-md-12 mb-3'),
                css_class='form-row'
            ),
            Row(
                Submit('submit', 'Complete', css_class='mb-4 mt-3 btn-lg'),
                css_class='form-row thanks-submit'
            ),
        )

    def set_language(self, replica):
        if replica.language == Replica.LANG_POR:
            self.fields['contactme'].label = "Marque a caixa ao lado caso aceite ser convidado para participar de outras pesquisas relacionadas à aplicação de tecnologia na promoção do envelhecimento saudável."
            self.helper.layout = Layout(
                Row(
                    Column('email', css_class='form-group col-md-8 mb-3 disabled'),
                    css_class='form-row'
                ),
                Row(
                    Column('contactme', css_class='form-group col-md-12 mb-3'),
                    css_class='form-row'
                ),
                Row(
                    Submit('submit', 'Concluir', css_class='mb-4 mt-3 btn-lg'),
                    css_class='form-row thanks-submit'
                ),
            )

class ScriptThanksExceptForm(ModelForm):
    script_id = IntegerField()
    class Meta:
        model = InterestedPerson
        fields = ['email', 'contactme', 'script_id']
        widgets = {
            'script_id': HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].label = "E-mail:"
        self.fields['contactme'].label = "Check this box if you agree to be invited to participate in other research related to technologies applied to promote healthy ageing."

        self.helper = FormHelper()
        self.helper.form_id = 'id-scriptthanksexceptform'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'finish'

        self.helper.layout = Layout(
            Field('script_id', type="hidden"),
            Row(
                Column('email', css_class='form-group col-md-8 mb-3 disabled'),
                css_class='form-row'
            ),
            Row(
                Column('contactme', css_class='form-group col-md-12 mb-3'),
                css_class='form-row'
            ),
            Row(
                Submit('submit', 'Complete', css_class='mb-4 mt-3 btn-lg'),
                css_class='form-row thanks-submit'
            ),
        )

    def set_language(self, replica):
        if replica.language == Replica.LANG_POR:
            self.fields['contactme'].label = "Marque a caixa ao lado caso aceite ser convidado para participar de outras pesquisas relacionadas à aplicação de tecnologia na promoção do envelhecimento saudável."
            self.helper.layout = Layout(
                Field('script_id', type="hidden"),
                Row(
                    Column('email', css_class='form-group col-md-8 mb-3 disabled'),
                    css_class='form-row'
                ),
                Row(
                    Column('contactme', css_class='form-group col-md-12 mb-3'),
                    css_class='form-row'
                ),
                Row(
                    Submit('submit', 'Concluir', css_class='mb-4 mt-3 btn-lg'),
                    css_class='form-row thanks-submit'
                ),
            )

class ScriptThanksForm(ModelForm):
    id = IntegerField()
    script_id = IntegerField()
    class Meta:
        model = Script
        fields = ['participant', 'contactme', 'comments', 'id', 'script_id']
        widgets = {
            'id': HiddenInput(),
            'script_id': HiddenInput(),
            'comments': Textarea(attrs={'rows': '5'}),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        if instance:
            self.initial['id'] = instance.id
            self.initial['script_id'] = instance.id

        self.fields['participant'].label = "E-mail:"
        self.fields['contactme'].label = "Check this box if you agree to be invited to participate in other research related to technologies applied to promote healthy ageing."
        self.fields['comments'].label = "Use the space below to leave any comments you may have to the researchers." 
        
        self.helper = FormHelper()
        self.helper.form_id = 'id-scriptthanksform'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'finish'

        self.helper.layout = Layout(
            Field('id', type="hidden"),
            Field('script_id', type="hidden"),
            Row(
                Column('participant', css_class='form-group col-md-8 mb-3 disabled'),
                css_class='form-row'
            ),
            Row(
                Column('contactme', css_class='form-group col-md-12 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('comments', css_class='form-group col-md-12 mb-3'),
                css_class='form-row'
            ),
            Row(
                Submit('submit', 'Complete', css_class='mb-4 mt-3 btn-lg'),
                css_class='form-row thanks-submit'
            ),
        )

    def set_language(self, replica):
        if replica.language == Replica.LANG_POR:
            self.fields['contactme'].label = "Marque a caixa ao lado caso aceite ser convidado para participar de outras pesquisas relacionadas à aplicação de tecnologia na promoção do envelhecimento saudável."
            self.fields['comments'].label = "Use o espaço abaixo para registrar quaisquer comentários que você queira deixar aos pesquisadores."
            
            self.helper.layout = Layout(
                Field('id', type="hidden"),
                Field('script_id', type="hidden"),
                Row(
                    Column('participant', css_class='form-group col-md-8 mb-3 disabled'),
                    css_class='form-row'
                ),
                Row(
                    Column('contactme', css_class='form-group col-md-12 mb-3'),
                    css_class='form-row'
                ),
                Row(
                    Column('comments', css_class='form-group col-md-12 mb-3'),
                    css_class='form-row'
                ),
                Row(
                    Submit('submit', 'Concluir', css_class='mb-4 mt-3 btn-lg'),
                    css_class='form-row thanks-submit'
                ),
            )

class StepForm(ModelForm):
    id = IntegerField()
    class Meta:
        model = Step
        fields = ['response', 'start', 'finish', 'id']
        widgets = {
            'id': HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super(StepForm, self).__init__(*args, **kwargs)
        if instance:
            self.initial['id'] = instance.id

    def clean_response(self):
        response = self.cleaned_data['response']
        if response is None:
            raise ValidationError(f"'Response cannot be empty.", code='invalid')
        return response

    def clean_start(self):
        new_start = self.cleaned_data['start']
        if self.instance.start is not None and self.instance.start > 0:
            return self.instance.start
        return new_start


class ScriptAdminForm(ModelForm):
    class Meta:
        widgets = { 
            'comments': Textarea(attrs={'rows': '5', 'cols': '95'}),
        }