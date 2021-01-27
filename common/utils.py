import random
import string
from django.utils.text import slugify
from PIL import Image
from html.parser import HTMLParser
from datetime import datetime, date, timedelta
import time
import threading
from threading import Thread
from django.core.mail import EmailMessage
import csv
from scripts.models import Script, Step, Component
from django.db import transaction
import os
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.sites.models import Site
from django.core.exceptions import AppRegistryNotReady

def resizeImage(path, x, y):
    img = Image.open(path)
    if img.height > x or img.width > y:
        output_size = (x, y)
        img.thumbnail(output_size)
        img.save(path)


class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        threading.Thread.__init__(self)

    def run (self):
        msg = EmailMessage(self.subject, self.html_content, to=self.recipient_list)
        msg.content_subtype = "html"
        msg.send()

def send_html_mail(subject, html_content, recipient_list):
    EmailThread(subject, html_content, recipient_list).start()


class UnicodeEntrypointValidator(UnicodeUsernameValidator):
    """Allows \."""
    message = 'Enter a valid entrypoint. This value may contain only letters, numbers, and @/./+/-/_ characters.'

validator_entrypoint = UnicodeEntrypointValidator()


def processReplicaScripts(scriptsFile, replica):
    try:
        reader = csv.DictReader(scriptsFile, delimiter='\t')
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:
        if hasattr(e, 'message'):
            return True, f'{e.message}', 0, 0
        else:
            return True, f'{e}', 0, 0
    # expected CSV structure:
    # Script    Step    Slot    Task Type   Oracle  Value
    last_script = None
    last_step = None
    last_script_num = 0
    last_step_num = 0
    _candidates = 0
    try:
        with transaction.atomic():
            for row in reader:
                # print(row['Script'], row['Step'], row['Slot'], row['Task Type'], row['Oracle'], row['Value'])
                _script, _step, _slot, _tasktype, _oracle, _value = row['Script'], row['Step'], row['Slot'], row['Task Type'], row['Oracle'], row['Value']
                if last_script_num != _script:
                    last_script = Script(replica=replica, script_num=_script, status=Script.STATUS_FREE, contactme=False, withdraw=False)
                    last_script.save()
                    last_script_num = _script
                    last_step = None
                    last_step_num = 0
                    _candidates = _candidates + 1
                if last_step_num != _step:
                    last_step = Step(script=last_script, step_num=_step, tasktype=_tasktype, oracle=_oracle)
                    last_step.save()
                    last_step_num = _step
                component = Component(step=last_step, slot_num=_slot, tasktype=_tasktype, value=_value)
                component.save()
    except KeyError:
        # rollback changes
        replica.scripts.all().delete()
        return True, 'Badly formed CSV file \n(expected: Script\tStep\tSlot\tTask Type\tOracle\tValue)', 0, 0
    except (KeyboardInterrupt, SystemExit):
        # rollback changes
        replica.scripts.all().delete()
        raise
    except Exception as e:
        # rollback changes
        replica.scripts.all().delete()
        if hasattr(e, 'message'):
            return True, f'{e.message}', 0, 0
        else:
            return True, f'{e}', 0, 0
    return False, '', _candidates, last_step_num


def generateReplicaResponsesFile(replica):
    rows = [
        ['Replica', 'Script', 'Step', 'Status', 'Participant', 'Contact Me', 'Withdraw', 'Task Type', 'Oracle', 'Response', 'Start', 'Finish']
    ]
    resp = Step.objects.filter(script__replica=replica).order_by('script__replica__entrypoint', 'script__script_num', 'step_num')
    resp = resp.values_list('script__replica__entrypoint', 'script__script_num', 'step_num', 'script__status', 'script__participant', 'script__contactme', 'script__withdraw', 'tasktype', 'oracle', 'response', 'start', 'finish')
    rows.extend(list(resp))
    filename = f"temp/{replica.entrypoint}_responses.csv"
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, 'w', newline='', encoding='utf-8') as fp:
        wr = csv.writer(fp, delimiter='\t', quoting=csv.QUOTE_NONE)
        wr.writerows(rows)
    buffer = open(filename, 'r', newline='', encoding='utf-8').read()
    os.unlink(filename)
    return buffer



class UtilitySiteSettings():

    def __init__(self):
        try:
            site = Site.objects.get_current()
            self.site_settings = site.settings
        except (AttributeError, KeyError, AppRegistryNotReady):
            # print('Warning! Site settings have not been initialized.')
            self.site_settings = None
        except:
            # print('Warning! Site settings have not been initialized.')
            self.site_settings = None

    def verifySettingsLoaded(self):
        if self.site_settings is None:
            try:
                site = Site.objects.get_current()
                self.site_settings = site.settings
                return True
            except (AttributeError, KeyError, AppRegistryNotReady):
                # print('Warning! Site settings have not been initialized.')
                return False
            except:
                return False
        return True

    def get_session_timeout(self):
        if self.verifySettingsLoaded():
            try:
                return self.site_settings.session_timeout
            except (AttributeError):
                # print('Warning! Site settings have not been initialized.')
                return 60
            except:
                return 60
        return 60  # minutes

    def get_session_timeout_seconds(self):
        return self.get_session_timeout()*60

uSiteSettings = UtilitySiteSettings()