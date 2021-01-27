from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.sites.models import Site
from django.utils import timezone
from .utils import processReplicaScripts, generateReplicaResponsesFile, send_html_mail
from studies.models import Replica, Image
from scripts.models import Script, Step, Component
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.utils import timezone
import os
from common.models import Setting
from django.core.exceptions import SuspiciousOperation

TEXT_ENG__ERR_404 = "Page Not Found"
TEXT_ENG__ERR_400 = "Bad Request"
TEXT_ENG__ERR_403 = "Permission Denied"
TEXT_ENG__ERR_500 = "Server Error"

TEXT_POR__ERR_404 = "Página não encontrada"
TEXT_POR__ERR_400 = "Requisição inválida"
TEXT_POR__ERR_403 = "Permissão negada"
TEXT_POR__ERR_500 = "Erro no servidor"

def home(request):
    context = {}    # provide 'extra_content' = True, to show extra content on homepage 
    if request.PREF_LANG == Setting.LANG_POR:
        return render(request, 'common/pt/home.pt.html', context)
    else:
        return render(request, 'common/en/home.en.html', context)


def handler404(request, exception):
    context = {}
    if request.PREF_LANG == Setting.LANG_POR:
        context['error'] = TEXT_POR__ERR_404
    else:
        context['error'] = TEXT_ENG__ERR_404
    return render(request, 'common/error.html', context)

def handler400(request, exception):
    context = {}
    if request.PREF_LANG == Setting.LANG_POR:
        context['error'] = TEXT_POR__ERR_400
    else:
        context['error'] = TEXT_ENG__ERR_400
    return render(request, 'common/error.html', context)

def handler403(request, exception):
    context = {}
    if request.PREF_LANG == Setting.LANG_POR:
        context['error'] = TEXT_POR__ERR_403
    else:
        context['error'] = TEXT_ENG__ERR_403
    return render(request, 'common/error.html', context)

def handler500(request):
    context = {}
    if request.PREF_LANG == Setting.LANG_POR:
        context['error'] = TEXT_POR__ERR_500
    else:
        context['error'] = TEXT_ENG__ERR_500
    return render(request, 'common/error.html', context)


#####################################
#   api calls:    replica_change    #
#####################################

def uploadScriptsFile_AJAX(request):
    # check authorization
    if not (request.method == "POST" and request.is_ajax() and request.user.is_authenticated):
        return JsonResponse({'error': True, 'message': f'Not authorized'})

    # parse form
    replica_id = None
    scriptsFile = None
    if 'replica' in request.POST and 'scriptsfile' in request.FILES:
        replica_id = request.POST['replica']
        try:
            scriptsFile = request.FILES['scriptsfile'].read().decode('utf-8').splitlines()
        except UnicodeDecodeError:
            errorTitle = f"Error while processing file '{request.FILES['scriptsfile'].name}'"
            return JsonResponse({'error': True, 'errorTitle': errorTitle, 'message': f'Invalid file'})
    else:
        return JsonResponse({'error': True, 'message': f'Invalid data'})
    if not scriptsFile:
        errorTitle = f"Error while processing file '{request.FILES['scriptsfile'].name}'"
        return JsonResponse({'error': True, 'errorTitle': errorTitle, 'message': f'Empty file'})
    if replica_id is None or replica_id == "" or scriptsFile is None:
        return JsonResponse({'error': True, 'message': f'Invalid data'})
    try:
        replica = Replica.objects.get(id=int(replica_id))
    except (Replica.DoesNotExist, ValueError):
        return JsonResponse({'error': True, 'message': f'Replica does not exist'})

    # test other stuff before allowing script addition
    if replica.status == Replica.STATUS_CANCELLED:
        return JsonResponse({'error': True, 'message': f'Action not allowed'})
    if replica.candidates is not None and replica.candidates > 0:
        return JsonResponse({'error': True, 'message': f'Action not allowed'})

    # process scripts file (updates db if transanction successful, else rolls back and returns error)
    error, message, candidates, taskcount = processReplicaScripts(scriptsFile, replica)

    if (error):
        errorTitle = f"Error while processing file '{request.FILES['scriptsfile'].name}'"
        return JsonResponse({'error': True, 'errorTitle': errorTitle, 'message': message})

    # update replica fields
    replica.candidates = candidates
    replica.numtasks = taskcount
    replica.filename = request.FILES['scriptsfile'].name
    replica.save()
    message = f"Successfully added {replica.scripts.count()} Scripts"
    data = {
        'error': False,
        'message': message,
        'replica_id': replica.id,
        'replica_status': replica.status,
        'replica_filename': replica.filename,
        'replica_candidates': replica.candidates,
        'replica_participants': replica.participants,
        'replica_tasks': replica.numtasks,
        'replica_images': replica.numimages,
    }
    return JsonResponse(data)


def resetReplica_AJAX(request):
    # check authorization
    if not (request.method == "POST" and request.is_ajax() and request.user.is_authenticated):
        return JsonResponse({'error': True, 'message': f'Not authorized'})

    # parse data
    replica_id = None
    if 'replica' in request.POST:
        replica_id = request.POST['replica']
    else:
        return JsonResponse({'error': True, 'message': f'Invalid data'})
    if replica_id is None or replica_id == "":
        return JsonResponse({'error': True, 'message': f'Invalid data'})
    try:
        replica = Replica.objects.get(id=int(replica_id))
    except (Replica.DoesNotExist, ValueError):
        return JsonResponse({'error': True, 'message': f'Replica does not exist'})

    # test other stuff before allowing reset
    if replica.status == Replica.STATUS_CANCELLED:
        return JsonResponse({'error': True, 'message': f'Action not allowed'})
    if (replica.numtasks is None or replica.numtasks == 0) and (replica.numimages is None or replica.numimages == 0):
        return JsonResponse({'error': True, 'message': f'Action not allowed'})

    # reset replica status, scripts, images, etc
    replica.scripts.all().delete()
    replica.images.all().delete()
    replica.status = Replica.STATUS_INACTIVE
    replica.filename = None
    replica.activated = None
    replica.completed = None
    replica.candidates = 0
    replica.participants = 0
    replica.numtasks = 0
    replica.numimages = 0
    replica.save()

    return JsonResponse({'error': False, 'message': f'Replica experiment scripts and images successfully reset'})

def uploadReplicaImages_AJAX(request):
    # check authorization
    if not (request.method == "POST" and request.is_ajax() and request.user.is_authenticated):
        return JsonResponse({'error': True, 'message': f'Not authorized'})

    # parse form
    replica_id = None
    if 'replica' in request.POST and 'images' in request.FILES:
        replica_id = request.POST['replica']
    else:
        return JsonResponse({'error': True, 'message': f'Invalid data'})
    if replica_id is None or replica_id == "":
        return JsonResponse({'error': True, 'message': f'Invalid data'})
    try:
        replica = Replica.objects.get(id=int(replica_id))
    except (Replica.DoesNotExist, ValueError):
        return JsonResponse({'error': True, 'message': f'Replica does not exist'})
    
    # other constraints
    if replica.status == Replica.STATUS_CANCELLED:
        return JsonResponse({'error': True, 'message': f'Action not allowed'})
    # only allowed if number of images is zero
    if replica.images.count() != 0:
        return JsonResponse({'error': True, 'message': f'Action not allowed'})

    # collect all images
    repl_imgs = []
    for f in request.FILES.getlist('images'):
        repl_imgs.append(Image(replica=replica, filename=f.name, content=f))
         
    if not repl_imgs:
        return JsonResponse({'error': True, 'message': f'Invalid data'})
    
    # bulk-add images to db
    Image.objects.bulk_create(repl_imgs)

    # update replica fields
    replica.numimages = replica.images.count()
    replica.save()
    if replica.numimages == 1:
        message = f"Successfully added 1 image to replica"
    else:
        message = f"Successfully added {replica.numimages} images to replica"
    data = {
        'error': False,
        'message': message,
        'replica_id': replica.id,
        'replica_status': replica.status,
        'replica_filename': replica.filename,
        'replica_candidates': replica.candidates,
        'replica_participants': replica.participants,
        'replica_tasks': replica.numtasks,
        'replica_images': replica.numimages,
    }
    return JsonResponse(data)


def updateReplicaStatus_AJAX(request):
    # check authorization
    if not (request.method == "POST" and request.is_ajax() and request.user.is_authenticated):
        return JsonResponse({'error': True, 'message': f'Not authorized'})

    # parse form
    replica_id = None
    new_status = None
    if 'replica' in request.POST and 'new_status' in request.POST:
        replica_id = request.POST['replica']
        new_status = request.POST['new_status']     # expected a status string
    else:
        return JsonResponse({'error': True, 'message': f'Invalid data'})
    if replica_id is None or replica_id == "" or new_status is None or new_status == "":
        return JsonResponse({'error': True, 'message': f'Invalid data'})
    try:
        replica = Replica.objects.get(id=int(replica_id))
    except (Replica.DoesNotExist, ValueError):
        return JsonResponse({'error': True, 'message': f'Replica does not exist'})

    # test if valid status option
    status_dict = dict(Replica.STATUS_CHOICES)
    if not any(new_status in sub for sub in status_dict):
        return JsonResponse({'error': True, 'message': f'Invalid status choice'})

    # assert status state machine conditions (researcher access)
    if new_status == Replica.STATUS_CANCELLED and replica.status == Replica.STATUS_INACTIVE:
            replica.status = new_status
    elif new_status == Replica.STATUS_ACTIVE and ((replica.status == Replica.STATUS_INACTIVE and replica.candidates > 0 and replica.numimages > 0) or replica.status == Replica.STATUS_SUSPENDED):
            replica.status = new_status
            replica.activated = timezone.now()
    elif new_status == Replica.STATUS_SUSPENDED and replica.status == Replica.STATUS_ACTIVE:
            replica.status = new_status
            replica.activated = None
    elif new_status == Replica.STATUS_CLOSED and replica.status == Replica.STATUS_SUSPENDED:
            replica.status = new_status
            replica.activated = None
    else:
        return JsonResponse({'error': True, 'message': f'Action not allowed'})

    # save replica changes
    replica.save()
    message = f"Successfully updated replica status to {Replica.STATUS_CHOICES[replica.status]}"
    data = {
        'error': False,
        'message': message,
        'replica_id': replica.id,
        'replica_status': replica.status,
        'replica_filename': replica.filename,
        'replica_candidates': replica.candidates,
        'replica_participants': replica.participants,
        'replica_tasks': replica.numtasks,
        'replica_images': replica.numimages,
    }
    return JsonResponse(data)    

def downloadReplicaResponses(request, entrypoint):
    if not request.user.is_authenticated:
        raise PermissionDenied()
    # get replica
    try:
        replica = Replica.objects.get(entrypoint=entrypoint)
    except Replica.DoesNotExist:
        raise Http404(f"Replica does not exist.")

    # test other stuff before allowing reset
    if not replica.candidates or not replica.scripts:
        return redirect('admin:studies_replica_change', replica.id)

    # generate reponses csv
    buffer = generateReplicaResponsesFile(replica)

    response = HttpResponse(buffer, content_type='text/csv')
    responses_filename = f'{os.path.splitext(replica.filename)[0]}_responses.csv'
    response['Content-Disposition'] = f'attachment; filename={responses_filename}'
    
    return response


def setPreferredLang(request, lang):
    rpath = request.GET.get('next', None)

    if rpath and not rpath.startswith('/set-lang/'):
        response = redirect(rpath)
    else:
        response = redirect('home')

    lang = lang.upper()
    if lang == Setting.LANG_POR:
        response.set_cookie("PREF_LANG", Setting.LANG_POR, max_age=10*365*24*60*60) 
    elif lang == Setting.LANG_ENG:
        response.set_cookie("PREF_LANG", Setting.LANG_ENG, max_age=10*365*24*60*60) 
    else:
        raise SuspiciousOperation

    return response