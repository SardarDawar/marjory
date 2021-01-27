from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
import json
from common.utils import uSiteSettings
from datetime import datetime

# cookie vars
PARTICIPATION_COOKIE_EXPIRE_DAYS = 10*365                          # 10 years
COMPLETED_COOKIE_EXPIRE_DAYS = PARTICIPATION_COOKIE_EXPIRE_DAYS    # 10 years
CONSENTED_COOKIE_EXPIRE_DAYS = PARTICIPATION_COOKIE_EXPIRE_DAYS    # 10 years

# if None is provided in LAST_RUN_SCRIPT it will be deleted
# if None is provided in PARTICIPATED_STUDIES, COMPLETED_STUDIES, they will be left as they were
def set_standard_cookies(response, LAST_RUN_SCRIPT, PARTICIPATED_STUDIES, COMPLETED_STUDIES):
    cookies_LAST_RUN_SCRIPT = None
    cookies_PARTICIPATED_STUDIES = {}
    cookies_COMPLETED_STUDIES = {}
    cookieVal = str(datetime.now().date())   

    if LAST_RUN_SCRIPT:
        cookies_LAST_RUN_SCRIPT = urlsafe_base64_encode(force_bytes(LAST_RUN_SCRIPT.id))
        response.set_cookie("LAST_RUN_SCRIPT", cookies_LAST_RUN_SCRIPT, max_age=uSiteSettings.get_session_timeout_seconds())
    else:
        response.delete_cookie("LAST_RUN_SCRIPT")

    if PARTICIPATED_STUDIES:
        for s in PARTICIPATED_STUDIES:
            sidb64 = urlsafe_base64_encode(force_bytes(s.id))
            cookies_PARTICIPATED_STUDIES[sidb64] = cookieVal
        cookies_PARTICIPATED_STUDIES = json.dumps(cookies_PARTICIPATED_STUDIES)
        response.set_cookie("PARTICIPATED_STUDIES", cookies_PARTICIPATED_STUDIES, max_age=PARTICIPATION_COOKIE_EXPIRE_DAYS*24*60*60)

    if COMPLETED_STUDIES:
        for s in COMPLETED_STUDIES:
            sidb64 = urlsafe_base64_encode(force_bytes(s.id))
            cookies_COMPLETED_STUDIES[sidb64] = cookieVal
        cookies_COMPLETED_STUDIES = json.dumps(cookies_COMPLETED_STUDIES)
        response.set_cookie("COMPLETED_STUDIES", cookies_COMPLETED_STUDIES, max_age=COMPLETED_COOKIE_EXPIRE_DAYS*24*60*60)

    return response

# if None is provided in CONSENTED_STUDIES, they will be left as they were
def set_consent_cookies(response, CONSENTED_STUDIES):
    cookies_CONSENTED_STUDIES = {}
    cookieVal = str(datetime.now().date())  

    if CONSENTED_STUDIES:
        for s in CONSENTED_STUDIES:
            sidb64 = urlsafe_base64_encode(force_bytes(s.id))
            cookies_CONSENTED_STUDIES[sidb64] = cookieVal
        cookies_CONSENTED_STUDIES = json.dumps(cookies_CONSENTED_STUDIES)
        response.set_cookie("CONSENTED_STUDIES", cookies_CONSENTED_STUDIES, max_age=CONSENTED_COOKIE_EXPIRE_DAYS*24*60*60)

    return response