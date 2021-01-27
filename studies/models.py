import os
from django.db import models
from common.storage import OverwriteStorage
from common.utils import resizeImage, validator_entrypoint
from django.template.defaultfilters import slugify
from scripts.models import Script
import datetime as dt
from django.db.models import DurationField, ExpressionWrapper, F
from common.utils import uSiteSettings


# glob vars
BASE_PATH = "studies"

def replicaImageSavePath(instance, filename):
    # study_ts = slugify(instance.replica.study.title)
    # study_fn = f"{instance.replica.study.id}-{study_ts[:25]}"
    return os.path.join(BASE_PATH, str(instance.replica.study.id), instance.replica.entrypoint, filename)

# not used
def replicaScriptSavePath(instance, filename):
    return os.path.join(BASE_PATH, instance.study, instance.entrypoint, filename)

class Study(models.Model):
    title = models.CharField(max_length=100)
    object = models.CharField(max_length=500)
    subject = models.CharField(max_length=500)
    objective = models.CharField(max_length=500)
    method = models.CharField(max_length=500)
    
    class Meta:
        verbose_name_plural = "Studies"
        ordering = ['title']

    def __str__(self):
        return f'{self.title}'

class Replica(models.Model):
    # language options
    LANG_ENG = 'EN'
    LANG_POR = 'PT'
    LANGUAGE_CHOICES = [
        (LANG_ENG, 'English'),
        (LANG_POR, 'Portuguese'),
    ]
    # status options
    STATUS_INACTIVE = 'INACTIVE'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_SUSPENDED = 'SUSPENDED'
    STATUS_CLOSED = 'CLOSED'
    STATUS_COMPLETED = 'COMPLETED'
    TEXT_STATUS_INACTIVE = 'Inactive'
    TEXT_STATUS_CANCELLED = 'Cancelled'
    TEXT_STATUS_ACTIVE = 'Active'
    TEXT_STATUS_SUSPENDED = 'Suspended'
    TEXT_STATUS_CLOSED = 'Closed'
    TEXT_STATUS_COMPLETED = 'Completed'
    STATUS_CHOICES = [
        (STATUS_INACTIVE, TEXT_STATUS_INACTIVE),
        (STATUS_CANCELLED, TEXT_STATUS_CANCELLED),
        (STATUS_ACTIVE, TEXT_STATUS_ACTIVE),
        (STATUS_SUSPENDED, TEXT_STATUS_SUSPENDED),
        (STATUS_CLOSED, TEXT_STATUS_CLOSED),
        (STATUS_COMPLETED, TEXT_STATUS_COMPLETED),
    ]
    # unallowed attribute values
    UNALLOWED_ENTRYPOINTS = ['admin', 'logout', 'favicon.ico']

    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="replicas")
    entrypoint = models.CharField(max_length=50, unique=True, validators=[validator_entrypoint,])
    title = models.CharField(max_length=100)
    profile = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default=LANG_POR)
    proponent = models.CharField(max_length=100)
    sponsor = models.CharField(max_length=100)
    approval = models.CharField(max_length=150)
    consent = models.TextField(max_length=5000)                               # models.CharField(max_length=5000)
    invitation = models.TextField(max_length=5000, blank=True, null=True)     # models.CharField(max_length=5000, blank=True, null=True)
    thanks = models.TextField(max_length=5000)                                # models.CharField(max_length=5000)
    redirect = models.TextField(max_length=5000)                              # models.CharField(max_length=5000)
    close = models.TextField(max_length=5000)                                 # models.CharField(max_length=5000)
    githubtag = models.CharField(max_length=20, blank=True, null=True)
    objective = models.CharField(max_length=50)
    save_uncompleted_scripts = models.BooleanField(default=False)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_INACTIVE)
    filename = models.CharField(max_length=50, null=True, blank=True)
    candidates = models.IntegerField(default=0)
    participants = models.IntegerField(default=0)
    numtasks = models.IntegerField(default=0)
    numimages = models.IntegerField(default=0)
    activated = models.DateTimeField(null=True, blank=True)
    completed = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['entrypoint']

    def get_valid_status_change_options(self):
        choices = []
        if self.status == Replica.STATUS_INACTIVE:
            choices.append((self.STATUS_INACTIVE, self.TEXT_STATUS_INACTIVE))
            choices.append((self.STATUS_CANCELLED, self.TEXT_STATUS_CANCELLED))
            if self.candidates > 0 and self.numimages > 0:
                choices.append((self.STATUS_ACTIVE, self.TEXT_STATUS_ACTIVE))
        elif self.status == Replica.STATUS_ACTIVE:
            choices.append((self.STATUS_ACTIVE, self.TEXT_STATUS_ACTIVE))
            choices.append((self.STATUS_SUSPENDED, self.TEXT_STATUS_SUSPENDED))
        elif self.status == Replica.STATUS_SUSPENDED:
            choices.append((self.STATUS_SUSPENDED, self.TEXT_STATUS_SUSPENDED))
            choices.append((self.STATUS_CLOSED, self.TEXT_STATUS_CLOSED))
            choices.append((self.STATUS_ACTIVE, self.TEXT_STATUS_ACTIVE))
        elif self.status == Replica.STATUS_CLOSED:
            choices.append((self.STATUS_CLOSED, self.TEXT_STATUS_CLOSED))
        elif self.status == Replica.STATUS_CANCELLED:
            choices.append((self.STATUS_CANCELLED, self.TEXT_STATUS_CANCELLED))
        elif self.status == Replica.STATUS_COMPLETED:
            choices.append((self.STATUS_COMPLETED, self.TEXT_STATUS_COMPLETED))
        return choices
 
    def save(self, *args, **kwargs): 
        if self.entrypoint in self.UNALLOWED_ENTRYPOINTS:
            raise ValueError(f"'{self.entrypoint}' is not allowed as entrypoint.")
        if self.status not in dict(self.STATUS_CHOICES).keys():
            raise ValueError(f"'{self.status}' is not a valid status option.")
        super(Replica, self).save(*args, **kwargs)
    
    def get_free_scripts(self):
        free_scripts = self.scripts.filter(status=Script.STATUS_FREE)
        return free_scripts.order_by('script_num') if free_scripts.count() > 0 else [None,]

    # returns allocated scripts for which (now() - script.start).seconds > session_timeout*60 seconds
    def get_allocated_uncompleted_scripts(self):
        allocated_scripts = self.scripts.filter(status=Script.STATUS_ALLOCATED)
        if allocated_scripts.count() > 0:
            # duration_expr = ExpressionWrapper(dt.datetime.now()-F('start'), output_field=DurationField())
            # allocated_scripts = allocated_scripts.annotate(duration=duration_expr)
            session_timeout_seconds = uSiteSettings.get_session_timeout_seconds()
            now_time = dt.datetime.now().replace(tzinfo=None)
            for s in allocated_scripts:
                # remove the ones which still have session time
                if (now_time - s.start.replace(tzinfo=None)).total_seconds() <= session_timeout_seconds:
                    allocated_scripts = allocated_scripts.exclude(id=s.id) 
            return allocated_scripts.order_by('script_num') if allocated_scripts.count() > 0 else [None,]
        return [None,]
    
    def hasFreeOrUncompletedScripts(self):
        free_script = self.get_free_scripts()[0]
        if free_script is None:
            uncompleted_script = self.get_allocated_uncompleted_scripts()[0]
            if uncompleted_script is None:
                return False
        return True
        
    def __str__(self):
        return f'{self.entrypoint}'

class Image(models.Model):
    replica = models.ForeignKey(Replica, on_delete=models.CASCADE, related_name="images")
    filename = models.CharField(max_length=100)
    content = models.ImageField(storage=OverwriteStorage(), upload_to=replicaImageSavePath, max_length=500)

    class Meta:
        ordering = ['replica__entrypoint', 'filename',]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resizeImage(self.content.path, 1000, 1000)

    def __str__(self):
        return f'[{self.replica.entrypoint}] - {self.filename}'