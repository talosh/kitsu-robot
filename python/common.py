from datetime import datetime
import os
import sys
import time
import uuid
import traceback
import subprocess

from pprint import pformat, pprint

def log(message):
    print ('[' + datetime.now().strftime("%Y%m%d %H:%M") + ']\n' + message + '\n')

def remote_listdir(path, config):
    cmd_ls_remote = [
            'ssh',
            config.get('server_user') + '@' + config.get('server_host'),
            'ls', '-1',
            path
            ]

    cmd_ls_remote_result = subprocess.run(cmd_ls_remote, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmd_ls_remote_result = cmd_ls_remote_result.stdout.decode()
    return cmd_ls_remote_result.split('\n')[:-1]

def apply_fields(string, fields):
    for k, v in fields.items():
        string = string.replace('{'+k+'}', str(v))
    return string

def flatten(current, key='', result={}):
    # Flatten dictionary and pre-format fields

    if isinstance(current, dict):
        for k in current:
            new_key = "{0}.{1}".format(key, k) if len(key) > 0 else k
            flatten(current[k], new_key, result)
    else:
        result[key] = current
    return result

def sanitize_name(name_to_sanitize):
    import re
    if name_to_sanitize is None:
        return None

    stripped_name = name_to_sanitize.strip()
    exp = re.compile(u'[^\w\.-]', re.UNICODE)

    result = exp.sub('_', stripped_name)
    return re.sub('_\_+', '_', result)