from django.forms import TextInput, Textarea, ModelForm, ValidationError
from .models import Replica
from django.utils import timezone

class StudyAdminForm(ModelForm):
    class Meta:
        widgets = { 
            'title': TextInput(attrs={'class':'special', 'size': '95'}),
            'object': Textarea(attrs={'rows': '5', 'cols': '95'}),
            'subject': Textarea(attrs={'rows': '5', 'cols': '95'}),
            'objective': Textarea(attrs={'rows': '5', 'cols': '95'}),
            'method': Textarea(attrs={'rows': '6', 'cols': '95'}),
        }

class ReplicaAdminForm(ModelForm):

    class Meta:
        fields = ('study','title', 'profile', 'source', 'language', 'proponent', 'sponsor', 'approval', 
                  'consent', 'invitation', 'thanks', 'redirect', 'close', 'githubtag', 'entrypoint', 
                  'objective', 'status',)
                  # 'save_uncompleted_scripts',
                  # 'filename', 'candidates', 'participants', 'numtasks', 'numimages',)
        labels = {
            'profile': ('Participant profile'),
            'source': ('Source of data'),
            'proponent': ('Proponent party'),
            'sponsor': ('Main sponsor'),
            'approval': ('Approval Process'),
            'githubtag': ('Github tag'),
            'entrypoint': ('Entry point'),
        }
        help_texts = {
            'consent': ('Please ensure that the content of this field contains a reference to the "Consent " button.'),
            'invitation': ('Please ensure that the content of this field contains a reference to the link to the research website.'),
        }
        widgets = { 
            # 'title': Textarea(attrs={'rows': '1', 'cols': '97', 'style':'resize:none;'}),
            'title': TextInput(attrs={'class':'special', 'size': '97'}),
            'profile': TextInput(attrs={'class':'special', 'size': '97'}),
            'source': TextInput(attrs={'class':'special', 'size': '97'}),
            'proponent': TextInput(attrs={'class':'special', 'size': '97'}),
            'sponsor': TextInput(attrs={'class':'special', 'size': '97'}),
            'approval': Textarea(attrs={'rows': '2', 'cols': '97', 'style':'resize:none;'}),
            'consent': Textarea(attrs={'rows': '10', 'cols': '97'}),
            'invitation': Textarea(attrs={'rows': '10', 'cols': '97'}),
            'thanks': Textarea(attrs={'rows': '10', 'cols': '97'}),
            'redirect': Textarea(attrs={'rows': '10', 'cols': '97'}),
            'close': Textarea(attrs={'rows': '10', 'cols': '97'}),
        }

    def __init__(self, *args, **kwargs):
        super(ReplicaAdminForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if 'status' in self.fields:
                self.fields['status'].choices = self.instance.get_valid_status_change_options()
            if 'entrypoint' in self.fields:
                self.fields['entrypoint'].disabled = True

    def clean_status(self):
        new_status = self.cleaned_data['status']
        # assert status state machine conditions (researcher access)
        # and update activated of instance
        if new_status == self.instance.status:
            return new_status
        elif new_status == Replica.STATUS_CANCELLED and self.instance.status == Replica.STATUS_INACTIVE:
            return new_status
        elif new_status == Replica.STATUS_ACTIVE and ((self.instance.status == Replica.STATUS_INACTIVE and self.instance.candidates > 0 and self.instance.numimages > 0) or self.instance.status == Replica.STATUS_SUSPENDED):
            self.instance.activated = timezone.now()
            return new_status
        elif new_status == Replica.STATUS_SUSPENDED and self.instance.status == Replica.STATUS_ACTIVE:
            self.instance.activated = None
            return new_status
        elif new_status == Replica.STATUS_CLOSED and self.instance.status == Replica.STATUS_SUSPENDED:
            self.instance.activated = None
            return new_status
        else:
            raise ValidationError(f'Select a valid status.', code='invalid')
        return new_status

    def clean_entrypoint(self):
        new_entrypoint = self.cleaned_data['entrypoint']
        print(new_entrypoint)
        if self.instance and self.instance.pk and self.instance.entrypoint and new_entrypoint != self.instance.entrypoint:
            raise ValidationError(f"Entrypoint cannot be changed.", code='invalid')
        if new_entrypoint in Replica.UNALLOWED_ENTRYPOINTS:
            raise ValidationError(f"'{new_entrypoint}' is not allowed as entrypoint.", code='invalid')
        return new_entrypoint