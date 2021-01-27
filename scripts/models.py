from django.db import models
import uuid

class Script(models.Model):
    # status options
    STATUS_FREE = 'FREE'
    STATUS_ALLOCATED = 'ALLOCATED'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CHOICES = [
        (STATUS_FREE, 'Free'),
        (STATUS_ALLOCATED, 'Allocated'),
        (STATUS_COMPLETED, 'Completed'),
    ]
    STATUS_CHOICES_DICT = dict(STATUS_CHOICES)
    replica = models.ForeignKey("studies.Replica", on_delete=models.CASCADE, related_name="scripts")
    script_num = models.IntegerField()
    start = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_FREE)
    participant = models.EmailField(null=True, blank=True)
    contactme = models.BooleanField()       # default: False
    comments = models.CharField(max_length=1000, null=True, blank=True)
    withdraw = models.BooleanField()        # default: False
    script_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        ordering = ['replica__entrypoint', 'script_num',]

    def get_status_string(self):
        return self.STATUS_CHOICES_DICT[self.status]

    def __str__(self):
        p = self.participant
        pt = f' ({p})' if p else ''
        return f'[{self.replica.entrypoint}] - ({self.script_num}) {{{self.script_uuid}}}{pt}'
    
    def save(self, *args, **kwargs): 
        if self.status == self.STATUS_FREE:
            self.start = None
            self.participant = None
            self.contactme = False
            self.withdraw = False
        if self.status == self.STATUS_ALLOCATED and self.start is None:
            raise ValueError(f"'Allocated script must have a start time.")
        super(Script, self).save(*args, **kwargs)
    
    def reset_script_steps(self):
        steps = self.steps.all()
        for step in steps:
            step.response = None
            step.start = None
            step.finish = None
        Step.objects.bulk_update(steps, ['response', 'start', 'finish'])
        self.status = self.STATUS_FREE
        self.start = None
        self.participant = None
        self.contactme = False
        self.withdraw = False
        self.save()

    def get_first_step(self):
        try:
            return self.steps.get(step_num=1)
        except Step.DoesNotExist:
            return None
        return None

    def get_next_step(self, prev_step_num):
        try:
            return self.steps.get(step_num=prev_step_num+1)
        except Step.DoesNotExist:
            return None
        return None
    
    def get_next_uncompleted_step(self, prev_step_num=None):
        uncompleted_steps = self.steps.filter(response=None)
        if uncompleted_steps.count() > 0:
            next_uncompleted_step = uncompleted_steps.order_by("step_num")[0]
            if prev_step_num:
                # step_num must be greater than prev_step_num
                if next_uncompleted_step.step_num > prev_step_num:
                    return next_uncompleted_step
            else:
                # just get first uncompleted step
                return next_uncompleted_step
        return None
    
    def is_last_step(self, step_num):
        return self.steps.count() == step_num

class Step(models.Model):
    script = models.ForeignKey(Script, on_delete=models.CASCADE, related_name="steps")
    step_num = models.IntegerField()
    tasktype = models.CharField(max_length=4)
    oracle = models.IntegerField()
    response = models.IntegerField(null=True, blank=True)
    start = models.BigIntegerField(null=True, blank=True)
    finish = models.BigIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['script__replica__entrypoint', 'script__script_num', 'step_num']

    def __str__(self):
        p = self.script.participant
        pt = f' ({p})' if p else ''
        return f'[{self.script.replica.entrypoint}] - ({self.script.script_num}.{self.step_num}){pt}'


class Component(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name="components")
    slot_num = models.IntegerField()
    tasktype = models.CharField(max_length=4)
    value = models.CharField(max_length=100)

    class Meta:
        ordering = ['step__script__replica__entrypoint', 'step__script__script_num', 'step__step_num', 'slot_num']

    def __str__(self):
        p = self.step.script.participant
        pt = f' ({p})' if p else ''
        return f'[{self.step.script.replica.entrypoint}] - ({self.step.script.script_num}.{self.step.step_num}.{self.slot_num}){pt}'

class InterestedPerson(models.Model):
    replica = models.ForeignKey("studies.Replica", on_delete=models.CASCADE, related_name="interested_persons")
    email = models.EmailField(null=True, blank=True)
    contactme = models.BooleanField()

    class Meta:
        ordering = ['replica__entrypoint',]
    
    def __str__(self):
        p = self.email
        pt = f' - ({p})' if p else ''
        return f'[{self.replica.entrypoint}]{pt}'

