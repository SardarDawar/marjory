from django.contrib import admin
from .models import Script, Step, Component, InterestedPerson
from .forms import ScriptAdminForm

class ScriptAdmin(admin.ModelAdmin):
    form = ScriptAdminForm

admin.site.register(Script, ScriptAdmin)
admin.site.register(Step)
admin.site.register(Component)
admin.site.register(InterestedPerson)
