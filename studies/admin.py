from django.contrib import admin
from .models import Study, Replica, Image
from django.contrib import admin
from django.db import models
from .forms import ReplicaAdminForm, StudyAdminForm

class StudyAdmin(admin.ModelAdmin):
    list_display = ('title',)
    change_form_template = 'admin/studies/study/study_change.html'
    form = StudyAdminForm

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['replicas'] = Study.objects.get(id=object_id).replicas.all()
        extra_context['replica_status_choices'] = dict(Replica.STATUS_CHOICES)
        return super(StudyAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

class ReplicaAdmin(admin.ModelAdmin):
    list_display = ('entrypoint', 'objective', '_date_activated', '_date_completed', '_profile_of_participants', 'candidates', 'participants', '_data_source', 'status')
    change_form_template = 'admin/studies/replica/replica_change.html'
    form = ReplicaAdminForm

    def _date_activated(self, obj):
        return obj.activated
    
    def _date_completed(self, obj):
        return obj.completed
    
    def _profile_of_participants(self, obj):
        return obj.profile
    
    def _data_source(self, obj):
        return obj.source
    
    _date_activated.short_description = 'Date Activated'
    _date_completed.short_description = 'Date Completed'
    _profile_of_participants.short_description = 'Profile of Participants'
    _data_source.short_description = 'Data Source'
    

    def add_view(self, request, extra_context=None):
        self.exclude = ('status', 'filename', 'candidates', 'participants', 'numtasks', 'numimages', 'activated', 'completed', 'save_uncompleted_scripts')
        return super(ReplicaAdmin,self).add_view(request)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.exclude = ('filename', 'candidates', 'participants', 'numtasks', 'numimages', 'activated', 'completed',  'save_uncompleted_scripts')
        extra_context = extra_context or {}
        replica = Replica.objects.get(id=object_id)
        extra_context['replica'] = replica
        return super(ReplicaAdmin,self).change_view(request, object_id, extra_context=extra_context)




admin.site.register(Study, StudyAdmin)
admin.site.register(Replica, ReplicaAdmin)
admin.site.register(Image)