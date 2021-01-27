
from django.urls import path, re_path
from .views import (scriptStart, scriptEPLinkStart, studyConfirmConsent, scriptTasks, scriptThanksExcept, scriptFinish,
                    setStepStartTime_AJAX,)
from .views import scriptCloseTemp

# url patterns under ('')
urlpatterns = [

    # urls (replica-entrypoint/scripts)
    path('<str:entrypoint>/', scriptStart, name='script-start'),
    path('s/load', scriptEPLinkStart, name='script-load'),
    path('<str:entrypoint>/consent', studyConfirmConsent, name='study-confirm-consent'),
    path('<str:entrypoint>/tasks', scriptTasks, name='tasks'),
    path('<str:entrypoint>/thanks', scriptThanksExcept, name='thanks-except'),
    path('<str:entrypoint>/finish', scriptFinish, name='finish'),
    # for debugging
    path('<str:entrypoint>/closetmp', scriptCloseTemp, name='close'),

    # step api calls
    path('api/step/set-start', setStepStartTime_AJAX, name='step-start-time'),
]
