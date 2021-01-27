from django.contrib.sessions.middleware import SessionMiddleware
from django.conf import settings
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from studies.models import Study
from scripts.models import Script
from django.contrib.sites.models import Site
import datetime as dt
import json
from common.models import Setting

class AppMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.
        self.session_timeout = 60
        site = Site.objects.get_current()
        try:
            site_settings = site.settings
            self.session_timeout = site_settings.session_timeout
        except AttributeError:
            pass

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if not request.path.startswith('/admin/'):
            # middleware runs only for non-admin pages
            request.PREF_LANG = Setting.LANG_ENG        # default frontend language
            request.PARTICIPATED_STUDIES = []
            request.COMPLETED_STUDIES = []
            request.CONSENTED_STUDIES = []              # list of studies for which user has visited the consent page
            request.LAST_RUN_SCRIPT = None

            # parse cookies
            # print(request.COOKIES)
            # are dictionaries
            cookies_PREF_LANG = request.COOKIES.get('PREF_LANG', None)
            cookies_PARTICIPATED_STUDIES = request.COOKIES.get('PARTICIPATED_STUDIES', None)
            cookies_COMPLETED_STUDIES = request.COOKIES.get('COMPLETED_STUDIES', None)
            cookies_CONSENTED_STUDIES = request.COOKIES.get('CONSENTED_STUDIES', None)
            cookies_LAST_RUN_SCRIPT = request.COOKIES.get('LAST_RUN_SCRIPT', None)

            # get user preferred lang
            if cookies_PREF_LANG:
                try:
                    cookies_PREF_LANG = str(cookies_PREF_LANG)
                    if (cookies_PREF_LANG == Setting.LANG_POR):
                        request.PREF_LANG = Setting.LANG_POR
                    # else it is kept LANG_ENG
                except(TypeError, ValueError):
                    pass
                except: 
                    pass

            # update PARTICIPATED_STUDIES and LAST_RUN_SCRIPT
            if cookies_PARTICIPATED_STUDIES:
                try:
                    cookies_PARTICIPATED_STUDIES = json.loads(cookies_PARTICIPATED_STUDIES)
                    for sidb64 in cookies_PARTICIPATED_STUDIES.keys():
                        try:
                            sid = force_text(urlsafe_base64_decode(sidb64))
                            study = Study.objects.get(pk=sid)
                            request.PARTICIPATED_STUDIES.append(study)
                        except(TypeError, ValueError, OverflowError, Study.DoesNotExist):
                            continue
                except json.decoder.JSONDecodeError:
                    pass
            
            if cookies_CONSENTED_STUDIES:
                try:
                    cookies_CONSENTED_STUDIES = json.loads(cookies_CONSENTED_STUDIES)
                    for sidb64 in cookies_CONSENTED_STUDIES.keys():
                        try:
                            sid = force_text(urlsafe_base64_decode(sidb64))
                            study = Study.objects.get(pk=sid)
                            request.CONSENTED_STUDIES.append(study)
                        except(TypeError, ValueError, OverflowError, Study.DoesNotExist):
                            continue
                        except:
                            continue
                except json.decoder.JSONDecodeError:
                    pass
                except:
                    pass

            if cookies_COMPLETED_STUDIES:
                try:
                    cookies_COMPLETED_STUDIES = json.loads(cookies_COMPLETED_STUDIES)
                    for sidb64 in cookies_COMPLETED_STUDIES.keys():
                        try:
                            sid = force_text(urlsafe_base64_decode(sidb64))
                            study = Study.objects.get(pk=sid)
                            request.COMPLETED_STUDIES.append(study)
                        except(TypeError, ValueError, OverflowError, Study.DoesNotExist):
                            continue
                        except:
                            continue
                except json.decoder.JSONDecodeError:
                    pass
                except:
                    pass

            if cookies_LAST_RUN_SCRIPT:
                LRS = None
                try:
                    sid = force_text(urlsafe_base64_decode(cookies_LAST_RUN_SCRIPT))
                    LRS = Script.objects.get(pk=sid)
                except(TypeError, ValueError, OverflowError, Script.DoesNotExist):
                    pass
                except:
                    pass

                # test if LAST_RUN_SCRIPT is in use and not expired
                if LRS and LRS.status == Script.STATUS_ALLOCATED and LRS.start:
                    if  LRS.replica.study in request.PARTICIPATED_STUDIES and LRS.replica.study not in request.COMPLETED_STUDIES:
                        if (dt.datetime.now().replace(tzinfo=None) - LRS.start.replace(tzinfo=None)).total_seconds() <= self.session_timeout*60:
                            # session for this script hasnt timed out
                            request.LAST_RUN_SCRIPT = LRS

        # view will update the cookies in reponse
        response = self.get_response(request)
        
        # Code to be executed for each request/response after
        # the view is called.
        return response