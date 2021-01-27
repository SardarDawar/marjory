from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.sites.models import Site
from django.utils import timezone
from studies.models import Replica, Image, Study
from scripts.models import Script, Step, Component
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, JsonResponse
from django.core.exceptions import SuspiciousOperation
from .forms import InterestedPersonForm, ScriptThanksForm, ScriptThanksExceptForm, StepForm

import datetime as dt
from common.utils import uSiteSettings
from django.db.models import Q
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .cookies import set_standard_cookies, set_consent_cookies

from .notifications import (getNotificationText, 
                            NOTIF_REPLICA_UNAVAILABLE, NOTIF_PARTICIPATION_INCOMPLETE, NOTIF_PARTICIPATION_ENDED, NOTIF_FAILED_LOAD_STEP, 
                            NOTIF_FAILED_LOAD_SCRIPT, NOTIF_ALREADY_PARTICIPATED,)

def scriptEPLinkStart(request):
    entrypoint_link = request.GET['epl']
    entrypoint_link_split = entrypoint_link.split('/') 
    # check only the last two elements in list
    if len(entrypoint_link_split) >= 1: 
        entrypoint = entrypoint_link_split[-1]
        if entrypoint in ["", "/"] and len(entrypoint_link_split) >= 2:
            entrypoint = entrypoint_link_split[-2]
        if entrypoint not in ["", "/"] and entrypoint not in Replica.UNALLOWED_ENTRYPOINTS:
            return redirect('script-start', entrypoint)
    raise SuspiciousOperation

def scriptStart(request, entrypoint):
    # get replica
    try:
        replica = Replica.objects.get(entrypoint=entrypoint)
    except Replica.DoesNotExist:
        raise SuspiciousOperation

    # test replica status
    if replica.status in [Replica.STATUS_INACTIVE, Replica.STATUS_CANCELLED, Replica.STATUS_SUSPENDED]:
        return notificationView(request, NOTIF_REPLICA_UNAVAILABLE)
    
    study = replica.study
    # test if study in COMPLETED_STUDIES
    # consent page not shown to people who have 'completed' the study
    if study in request.COMPLETED_STUDIES:
        return notificationView(request, NOTIF_ALREADY_PARTICIPATED)
    
    # USER MUST SEE CONTENT PAGE REGARDLESS OF PREVIOUS PARTICIPATION, if they visited this page
    # so they could be forwarded to thanks-except if no scripts are available for replica
    
    if replica.language == Replica.LANG_POR:
        return render(request, 'studies/pt/consent.pt.html', {'replica': replica})
    else:
        return render(request, 'studies/en/consent.en.html', {'replica': replica})

def studyConfirmConsent(request, entrypoint):
    # get replica
    try:
        replica = Replica.objects.get(entrypoint=entrypoint)
    except Replica.DoesNotExist:
        raise SuspiciousOperation

    # test replica status
    if replica.status in [Replica.STATUS_INACTIVE, Replica.STATUS_CANCELLED, Replica.STATUS_SUSPENDED]:
        return notificationView(request, NOTIF_REPLICA_UNAVAILABLE)

    if request.method == 'POST':
        study_id = None
        try:
            study_id = request.POST['study_id']
            study_id = int(study_id)
            study = Study.objects.get(id=study_id)
        except (ValueError, KeyError, Study.DoesNotExist):
            raise SuspiciousOperation
        # study in form must be [url]replica.study
        if study != replica.study:
            raise SuspiciousOperation
        # confirm consent if not already done
        if study not in request.CONSENTED_STUDIES:
            request.CONSENTED_STUDIES.append(study)
        # this page will will allocate a script (if available)
        response = redirect('tasks', replica.entrypoint)
        # cookies updated, so set them in response
        return set_consent_cookies(response, request.CONSENTED_STUDIES)
    else:
        # cannot 'GET' to this page
        raise SuspiciousOperation

def scriptThanksExcept(request, entrypoint):
    # get replica
    try:
        replica = Replica.objects.get(entrypoint=entrypoint)
    except Replica.DoesNotExist:
        raise SuspiciousOperation
    
    study = replica.study
    
    if study not in request.CONSENTED_STUDIES:
        # cookies have to be enabled to continue beyond this point
        # also, user must first visit the consent page (at least once)
        return redirect('script-start', entrypoint)     # consent page

    if study in request.COMPLETED_STUDIES:
        return notificationView(request, NOTIF_ALREADY_PARTICIPATED)
    elif study in request.PARTICIPATED_STUDIES:
        # user participated in this study but did not complete it, is accessing Thanks page
        # do not allow creation of InterestedPerson object
        # check if they have a last_run_script and if it is still valid
        if request.LAST_RUN_SCRIPT and request.LAST_RUN_SCRIPT in replica.scripts.all() and request.LAST_RUN_SCRIPT.status == Script.STATUS_ALLOCATED and hasScriptRemainingTime(request.LAST_RUN_SCRIPT):
            # indicate that resuming participation might be possible (although not necessarily for this person)
            return notificationView(request, NOTIF_PARTICIPATION_INCOMPLETE)
        else:
            # particiption could not be resumed, consider it finished
            return notificationView(request, NOTIF_PARTICIPATION_ENDED)

    # test replica status
    if replica.status in [Replica.STATUS_INACTIVE, Replica.STATUS_CANCELLED, Replica.STATUS_SUSPENDED]:
        return notificationView(request, NOTIF_REPLICA_UNAVAILABLE) 
    # elif replica.status in [Replica.STATUS_CLOSED, Replica.STATUS_COMPLETED]:
    else:
        # if replica status is active and replica has remaining scripts
        if replica.status == Replica.STATUS_ACTIVE and replica.hasFreeOrUncompletedScripts():
            return redirect('script-start', replica)
        # else return thanks-except form 
        if request.method == 'POST':
            form = InterestedPersonForm(request.POST)
            form.set_language(replica)
            if form.is_valid():
                email = form.cleaned_data.get('email')
                if email:
                    form.instance.replica = replica
                    form.save(commit=True)
                # return redirect('home')
                if replica.language == Replica.LANG_POR:
                    return render(request, 'studies/pt/close.pt.html', {'replica': replica})
                else:
                    return render(request, 'studies/en/close.en.html', {'replica': replica})
        else:
            form = InterestedPersonForm()
            form.set_language(replica)
        if replica.language == Replica.LANG_POR:
            return render(request, 'studies/pt/thanks_except.pt.html', {'replica': replica, 'form': form})
        else:
            return render(request, 'studies/en/thanks_except.en.html', {'replica': replica, 'form': form})
    return redirect('home')


# for debugging purposes
#########################################
def scriptCloseTemp(request, entrypoint):
    # get replica
    try:
        replica = Replica.objects.get(entrypoint=entrypoint)
    except Replica.DoesNotExist:
        raise SuspiciousOperation
    # test replica status
    if replica.status in [Replica.STATUS_INACTIVE, Replica.STATUS_CANCELLED, Replica.STATUS_SUSPENDED]:
        return notificationView(request, NOTIF_REPLICA_UNAVAILABLE)
    if request.method == 'POST':
        script_id = None
        try:
            script_id = request.POST['id']
            script_id = int(script_id)
        except (ValueError, KeyError):
            raise SuspiciousOperation
        script = get_object_or_404(Step, id=script_id)
        form = ScriptThanksForm(request.POST, instance=script)
        form.set_language(replica)
        if form.is_valid():
            form.save(commit=True)
            if replica.language == Replica.LANG_POR:
                response = render(request, 'studies/pt/close.pt.html', {'replica': replica})
            else:
                response = render(request, 'studies/en/close.en.html', {'replica': replica})
            # remove last run script
            return set_standard_cookies(response, None, None, None)
        if replica.language == Replica.LANG_POR:
            return render(request, 'studies/pt/thanks.pt.html', {'replica': replica, 'form': form})
        else:
            return render(request, 'studies/en/thanks.en.html', {'replica': replica, 'form': form})
    else:
        script = replica.scripts.get(script_num=1)
        # send script finish form
        form = ScriptThanksForm(instance=script)
        form.set_language(replica)
        request.LAST_RUN_SCRIPT = None
        # request.COMPLETED_STUDIES.append(script.replica.study)
        if script.replica.language == Replica.LANG_POR:
            response = render(request, 'studies/pt/thanks.pt.html', {'replica': script.replica, 'script': script, 'form': form})
        else:
            response = render(request, 'studies/en/thanks.en.html', {'replica': script.replica, 'script': script, 'form': form})
        return set_standard_cookies(response, request.LAST_RUN_SCRIPT, None, request.COMPLETED_STUDIES)
    return redirect('home')
#########################################

def scriptFinish(request, entrypoint):
    # get replica
    try:
        replica = Replica.objects.get(entrypoint=entrypoint)
    except Replica.DoesNotExist:
        raise SuspiciousOperation
    # test replica status
    if replica.status in [Replica.STATUS_INACTIVE, Replica.STATUS_CANCELLED, Replica.STATUS_SUSPENDED]:
        return notificationView(request, NOTIF_REPLICA_UNAVAILABLE)

    if request.method == 'POST':
        script_id = None
        try:
            script_id = request.POST['script_id']       # must be in both ScriptThanks and ScriptThanksExcept form
            script_id = int(script_id)
        except (ValueError, KeyError):
            raise SuspiciousOperation
        script = get_object_or_404(Script, id=script_id)

        # script must be of replice in entrypoint
        if script.replica != replica:
            raise SuspiciousOperation

        # check study completion/participation
        study = script.replica.study
        if study not in request.COMPLETED_STUDIES:
            # user did not complete this script
            if study not in request.PARTICIPATED_STUDIES:
                raise SuspiciousOperation
            # user has participated but not completed script (form should be a ScriptThanksExcept form)
            # following handle case: participated but not completed (session timed-out + auto-submit)
            try:
                form = ScriptThanksExceptForm(request.POST)
            except:
                raise SuspiciousOperation
            form.set_language(replica)
            if form.is_valid():
                email = form.cleaned_data.get('email')
                if email:
                    form.instance.replica = replica
                    form.save(commit=True)
                # response = redirect('home')
                # alt response:
                if replica.language == Replica.LANG_POR:
                    response = render(request, 'studies/pt/close.pt.html', {'replica': replica})
                else:
                    response = render(request, 'studies/en/close.en.html', {'replica': replica})
                return set_standard_cookies(response, None, None, None)         # removes last run script (just in case)
            # invalid form data, resend invalide form
            if replica.language == Replica.LANG_POR:
                return render(request, 'studies/pt/thanks_except.pt.html', {'replica': replica, 'script': script, 'form': form})
            else:
                return render(request, 'studies/en/thanks_except.en.html', {'replica': replica, 'script': script, 'form': form})

        # participant must have completed the script
        # check script completion
        if script.status != Script.STATUS_COMPLETED:
            return SuspiciousOperation
        form = ScriptThanksForm(request.POST, instance=script)
        form.set_language(replica)
        if form.is_valid():
            # script status must not be free to make the following changes to db
            form.save(commit=True)
            if replica.language == Replica.LANG_POR:
                response = render(request, 'studies/pt/close.pt.html', {'replica': replica})
            else:
                response = render(request, 'studies/en/close.en.html', {'replica': replica})
            # remove last run script (just in case)
            return set_standard_cookies(response, None, None, None)
        if replica.language == Replica.LANG_POR:
            return render(request, 'studies/pt/thanks.pt.html', {'replica': replica, 'script': script, 'form': form})
        else:
            return render(request, 'studies/en/thanks.en.html', {'replica': replica, 'script': script, 'form': form})
    else:
        # cannot 'GET' to this page
        raise SuspiciousOperation

    return redirect('home')

def scriptTasks(request, entrypoint):
    # get replica
    try:
        replica = Replica.objects.get(entrypoint=entrypoint)
    except Replica.DoesNotExist:
        raise SuspiciousOperation

    # test replica status
    if replica.status in [Replica.STATUS_INACTIVE, Replica.STATUS_CANCELLED, Replica.STATUS_SUSPENDED]:
        return notificationView(request, NOTIF_REPLICA_UNAVAILABLE) 

    if replica.status in [Replica.STATUS_CLOSED, Replica.STATUS_COMPLETED]:
        return redirect('thanks-except', replica.entrypoint)

    study = replica.study
    if study in request.COMPLETED_STUDIES:
        return notificationView(request, NOTIF_ALREADY_PARTICIPATED)

    if study not in request.CONSENTED_STUDIES:
        # cookies have to be enabled to continue beyond this point
        # also, user must first visit the consent page (at least once)
        return redirect('script-start', entrypoint)     # consent page

    if request.method == 'POST':
        # get the task form
        step_id = None
        try:
            step_id = request.POST['id']
            step_id = int(step_id)
        except (ValueError, KeyError):
            raise SuspiciousOperation
        step = get_object_or_404(Step, id=step_id)
        form = StepForm(request.POST, instance=step)
        script = step.script
        # test script session and status            
        if script.status == Script.STATUS_ALLOCATED: 
            if hasScriptRemainingTime(script):
                if form.is_valid():
                    # save and update db
                    form.save(commit=True)
                    step = script.get_next_step(prev_step_num=step.step_num)
                    if step is None: 
                        if script.steps.count() > 0:
                            # all steps have been finished, set script state to completed
                            scriptPreFinish(script)
                            # send script finish form
                            form = ScriptThanksForm(instance=script)
                            form.set_language(replica)
                            request.LAST_RUN_SCRIPT = None
                            request.COMPLETED_STUDIES.append(script.replica.study)
                            if script.replica.language == Replica.LANG_POR:
                                response = render(request, 'studies/pt/thanks.pt.html', {'replica': script.replica, 'script': script, 'form': form})
                            else:
                                response = render(request, 'studies/en/thanks.en.html', {'replica': script.replica, 'script': script, 'form': form})
                            return set_standard_cookies(response, request.LAST_RUN_SCRIPT, None, request.COMPLETED_STUDIES)

                        else:
                            # no steps in script
                            return notificationView(request, NOTIF_FAILED_LOAD_SCRIPT)
                    # new form
                    form = StepForm(instance=step)
                remaining_session_seconds = getScriptRemainingSeconds(script)
                return get_step_page(request, step, form, remaining_session_seconds)
            else:
                # time has run out
                # considering the received response (if any), of current task, to be due to auto-submit, and hence not saving it
                if script.replica.save_uncompleted_scripts:         # defaults to False
                    # save script and consider it completed (the much which is done)
                    scriptPreFinish(script)         # now the script status would be set to completed
                    # send script finish form
                    form = ScriptThanksForm(instance=script)
                    form.set_language(replica)
                    request.LAST_RUN_SCRIPT = None
                    request.COMPLETED_STUDIES.append(script.replica.study)
                    if script.replica.language == Replica.LANG_POR:
                        response = render(request, 'studies/pt/thanks.pt.html', {'replica': script.replica, 'script': script, 'form': form})
                    else:
                        response = render(request, 'studies/en/thanks.en.html', {'replica': script.replica, 'script': script, 'form': form})
                    return set_standard_cookies(response, request.LAST_RUN_SCRIPT, None, request.COMPLETED_STUDIES)
                else:
                    # DEFAULT BEHAVIOUR
                    # uncompleted script submitted through auto-submit at timeout,
                    # is not to be set to COMPLETED, script status remains ALLOCATED
                    # send the User Script-Thanks-Except form (action 'finish')
                    # must have this study in PARTICIPATED_STUDIES (but not in COMPLETED_STUDIES) for right logic execution in 'finish' page
                    form = ScriptThanksExceptForm(initial={'script_id': script.id})
                    form.set_language(replica)
                    if script.replica.language == Replica.LANG_POR:
                        response = render(request, 'studies/pt/thanks_except.pt.html', {'replica': script.replica, 'script': script, 'form': form})
                    else:
                        response = render(request, 'studies/en/thanks_except.en.html', {'replica': script.replica, 'script': script, 'form': form})
                    return set_standard_cookies(response, None, None, None)     # this will remove last_run_script from cookies

        else:
            # cannot post data to a free/completed script's steps
            raise SuspiciousOperation
        pass
    else:       # get request
        if request.LAST_RUN_SCRIPT and request.LAST_RUN_SCRIPT in replica.scripts.all():
            # last run script is of this replica i.e. request.LAST_RUN_SCRIPT.replica.study == replica.study
            # user says to have run a script of this replica before 
            if study in request.PARTICIPATED_STUDIES and study not in request.COMPLETED_STUDIES:
                script = request.LAST_RUN_SCRIPT
                # check script session and status
                if script.status == Script.STATUS_ALLOCATED and hasScriptRemainingTime(script):
                    # only an allocated script can be allowed to be continued
                    # script still has remaining time
                    step = script.get_next_uncompleted_step()
                    if step is None: 
                        if script.steps.count() > 0:
                            # all steps have been finished, script state should have been finished (error recovery)
                            scriptPreFinish(script)
                            # send script finish form
                            form = ScriptThanksForm(instance=script)
                            request.LAST_RUN_SCRIPT = None
                            request.COMPLETED_STUDIES.append(script.replica.study)
                            if script.replica.language == Replica.LANG_POR:
                                response = render(request, 'studies/pt/thanks.pt.html', {'replica': script.replica, 'script': script, 'form': form})
                            else:
                                response = render(request, 'studies/en/thanks.en.html', {'replica': script.replica, 'script': script, 'form': form})
                            return set_standard_cookies(response, request.LAST_RUN_SCRIPT, None, request.COMPLETED_STUDIES)

                        else:
                            # no steps in script
                            return notificationView(request, NOTIF_FAILED_LOAD_SCRIPT)
                    else:
                        # send next step to user, no cookie updates
                        remaining_session_seconds = getScriptRemainingSeconds(script)
                        return get_step_page(request, step, StepForm(instance=step), remaining_session_seconds)
                else:
                    response = notificationView(request, NOTIF_PARTICIPATION_ENDED)
                    return set_standard_cookies(response, None, None, None)     # this will remove last_run_script from cookies
            else:
                # claims to be continuing script but doesn't have a record of participation/completion
                raise SuspiciousOperation
        else:
            # if user has already participated in this study (but doesn't have a record of the last run script), do not allocate a new script for them
            if study in request.PARTICIPATED_STUDIES:
                # if participated and 'GETTING' here last run script must have timed out
                return notificationView(request, NOTIF_PARTICIPATION_ENDED)
            # try to allot a new script to user
            new_script = replica.get_free_scripts()[0]
            if new_script is None:
                new_script = replica.get_allocated_uncompleted_scripts()[0]
                if new_script is None:
                    return redirect('thanks-except', replica)
                else:
                    # reset script to be free, and reset steps response
                    new_script.reset_script_steps()
                    # continue to allocate freed script to participant
            # make sure the script has steps
            if new_script.steps.count() == 0:
                return notificationView(request, NOTIF_FAILED_LOAD_SCRIPT)
            # we have a new free script, allocate it
            new_script.status = Script.STATUS_ALLOCATED
            new_script.start = dt.datetime.now()
            new_script.save()
            remaining_session_seconds = getScriptRemainingSeconds(new_script)
            # send script's first step (form+components)
            step = new_script.get_first_step()
            if step is None:
                return notificationView(request, NOTIF_FAILED_LOAD_SCRIPT)
            request.LAST_RUN_SCRIPT = new_script
            request.PARTICIPATED_STUDIES.append(new_script.replica.study)
            response = get_step_page(request, step, StepForm(instance=step), remaining_session_seconds)
            # cookies updated, so set them in response
            return set_standard_cookies(response, request.LAST_RUN_SCRIPT, request.PARTICIPATED_STUDIES, None)
        return redirect('script-start', replica)    # consent page


# task-type string dependent
def get_step_page(request, step, form, remaining_session_seconds):
    if step.tasktype.casefold() == 'tt01':
        try:
            slot1 = step.components.get(slot_num=1)
            slot2 = step.components.get(slot_num=2)
            slot3 = step.components.get(slot_num=3)
            slot4 = step.components.get(slot_num=4)
        except Component.DoesNotExist:
            return notificationView(request, NOTIF_FAILED_LOAD_STEP)
        # slots 2 and 4 are images, try to get them
        images = step.script.replica.images
        try:
            slot2 = images.get(filename=slot2.value)
            slot4 = images.get(filename=slot4.value)
        except Image.DoesNotExist:
            return notificationView(request, NOTIF_FAILED_LOAD_STEP)
        context = {
            'slot1': slot1, 'slot2': slot2, 'slot3': slot3, 'slot4': slot4,
            'form': form,
            'remaining_session_seconds': remaining_session_seconds,
            'replica': step.script.replica,
            'step': step,
        }
        if step.script.replica.language == Replica.LANG_POR:
            return render(request, "scripts/pt/tt01.pt.html", context)
        else:
            return render(request, "scripts/en/tt01.en.html", context)

    elif step.tasktype.casefold() == 'tt02':
        try:
            slot1 = step.components.get(slot_num=1)
            slot2 = step.components.get(slot_num=2)
            slot3 = step.components.get(slot_num=3)
            slot4 = step.components.get(slot_num=4)
            slot5 = step.components.get(slot_num=5)
            slot6 = step.components.get(slot_num=6)
            slot7 = step.components.get(slot_num=7)
            slot8 = step.components.get(slot_num=8)
            slot9 = step.components.get(slot_num=9)
            slot10 = step.components.get(slot_num=10)
        except Component.DoesNotExist:
            return notificationView(request, NOTIF_FAILED_LOAD_STEP)
        # slots 2 4 5 9 10 are images, try to get them
        images = step.script.replica.images
        try:
            slot2 = images.get(filename=slot2.value)
            slot4 = images.get(filename=slot4.value)
            slot5 = images.get(filename=slot5.value)
            slot9 = images.get(filename=slot9.value)
            slot10 = images.get(filename=slot10.value)
        except Image.DoesNotExist:
            return notificationView(request, NOTIF_FAILED_LOAD_STEP)
        context = {
            'slot1': slot1, 'slot2': slot2, 'slot3': slot3, 'slot4': slot4, 'slot5': slot5, 'slot6': slot6, 'slot7': slot7, 'slot8': slot8, 'slot9': slot9, 'slot10': slot10,
            'form': form,
            'remaining_session_seconds': remaining_session_seconds,\
            'replica': step.script.replica,
            'step': step,
        }
        if step.script.replica.language == Replica.LANG_POR:
            return render(request, "scripts/pt/tt02.pt.html", context)
        else:
            return render(request, "scripts/en/tt02.en.html", context)
    else:
        return notificationView(request, NOTIF_FAILED_LOAD_STEP)


def notificationView(request, notif_id):
    return render(request, 'common/notification.html', context = {
        'message': getNotificationText(notif_id, request.PREF_LANG),
    })

def setStepStartTime_AJAX(request):
    # check authorization
    if not (request.method == "POST" and request.is_ajax()):
        return JsonResponse({'error': True, 'message': f'Not authorized'})

    # parse form
    step_id = None
    step_start = None
    if 'step_id' in request.POST and 'step_start' in request.POST:
        step_id = request.POST['step_id']
        step_start = request.POST['step_start']     # expected a big int
    else:
        return JsonResponse({'error': True, 'message': f'Invalid data'})
    if step_id is None or step_id == "" or step_start is None or step_start == "":
        return JsonResponse({'error': True, 'message': f'Invalid data'})
    try:
        step = Step.objects.get(id=int(step_id))
    except (Step.DoesNotExist, ValueError):
        return JsonResponse({'error': True, 'message': f'Step does not exist'})

    # test if valid start int
    try:
        step_start = int(step_start)
    except ValueError:
        return JsonResponse({'error': True, 'message': f'Invalid data'})

    # assert start cannot be changed once validly set
    if step.start is not None and step.start > 0:
        data = {
            'error': True,
            'message': "Step start time already set.",
            'step_start': step.start,
        }
    else:
        step.start = step_start
        step.save()
        data = {
            'error': False,
            'message': "Step start successfully set.",
            'step_start': step.start,
        }
    return JsonResponse(data)  



# scripts utility functions
def hasScriptRemainingTime(script):
    return (dt.datetime.now().replace(tzinfo=None) - script.start.replace(tzinfo=None)).total_seconds() <= uSiteSettings.get_session_timeout_seconds()

def getScriptRemainingSeconds(script):
    script_session_end_time = script.start + dt.timedelta(seconds=uSiteSettings.get_session_timeout_seconds())
    return (script_session_end_time.replace(tzinfo=None) - dt.datetime.now().replace(tzinfo=None)).total_seconds()

def scriptPreFinish(script):
    script.status = Script.STATUS_COMPLETED
    script.save()
    replica = script.replica
    replica.participants = replica.scripts.filter(status=Script.STATUS_COMPLETED).count()
    # check if all replica scripts has COMPLETED status
    uncompleted_scripts = replica.scripts.filter(~Q(status=Script.STATUS_COMPLETED))
    if uncompleted_scripts.count() == 0:
        # all scripts have completed, replica is completed
        replica.status = Replica.STATUS_COMPLETED
        replica.completed = timezone.now()
    replica.save()