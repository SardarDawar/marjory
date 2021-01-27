
from django.urls import path, re_path
from .views import (home, 
                    uploadScriptsFile_AJAX, resetReplica_AJAX, uploadReplicaImages_AJAX, updateReplicaStatus_AJAX,
                    downloadReplicaResponses,
                    setPreferredLang)

# url patterns under ('')
urlpatterns = [

    # base site urls
    path('', home, name='home'),
    # base site request-redirect urls
    path('set-lang/<str:lang>', setPreferredLang, name='set-lang'),

    # api urls (replica)
    path('api/replica/scriptsfile-upload', uploadScriptsFile_AJAX, name='scriptsfile-upload'),
    path('api/replica/images-upload', uploadReplicaImages_AJAX, name='images-upload'),
    path('api/replica/reset', resetReplica_AJAX, name='replica-reset'),
    # path('api/replica/update-status', updateReplicaStatus_AJAX, name='status-update'),
    path('api/replica/<str:entrypoint>/download-responses', downloadReplicaResponses, name='responses-download'),
]
