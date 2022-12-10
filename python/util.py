import os
import sys
import subprocess
from datetime import datetime
from pprint import pprint, pformat


class RobotLog(object):
    def __init__(self, *args, **kwargs) -> None:
        if len(args) == 0:
            config_data = {}
        else:
            config_data = args[0]
            
        self.app_name = config_data.get('app_name', 'myApp')
        self.is_verbose = config_data.get('verbose', False)
        self.is_debug = config_data.get('debug', False)

        if config_data.get('log_folder') and kwargs.get('filename'):
            logfile_path = os.path.join(
                config_data.get('log_folder'), 
                kwargs.get('filename')
                )
            try:
                self.logfile = open(logfile_path,'a')
            except:
                self.error('Can not open log file %s' % logfile_path)
                self.logfile = None

    def timestamp():
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        return timestamp

    def msg(self, message):
        msg = '[%s] [%s] %s' % (self.timestamp(), self.app_name, message)
        print (msg)
        if self.logfile:
            try:
                self.logfile.write(msg + '\n')
                self.logfile.flush()
            except:
                pass

    def info(self, message):
        msg = '[%s] [%s] [INFO]: %s' % (self.timestamp(), self.app_name, message)
        print (msg)
        if self.logfile:
            try:
                self.logfile.write(msg + '\n')
                self.logfile.flush()
            except:
                pass

    def warning(self, message):
        msg = '[%s] [%s] [WARNING]: %s' % (self.timestamp(), self.app_name, message)
        print (msg)
        if self.logfile:
            try:
                self.logfile.write(msg + '\n')
                self.logfile.flush()
            except:
                pass

    def error(self, message):
        msg = '[%s] [%s] [ERROR]: %s' % (self.timestamp(), self.app_name, message)
        print (msg)
        if self.logfile:
            try:
                self.logfile.write(msg + '\n')
                self.logfile.flush()
            except:
                pass

    def verbose(self, message):
        if not self.is_verbose:
            return

        msg = '[%s] [%s] [VERBOSE]: %s' % (self.timestamp(), self.app_name, message)
        print (msg)
        if self.logfile:
            try:
                self.logfile.write(msg + '\n')
                self.logfile.flush()
            except:
                pass

    def debug(self, message):
        if not self.is_debug:
            return

        msg = '[%s] [%s] [DEBUG]: %s' % (self.timestamp(), self.app_name, message)
        print (msg)
        if self.logfile:
            try:
                self.logfile.write(msg + '\n')
                self.logfile.flush()
            except:
                pass

def create_timestamp():
    # generates UUID for the batch setup
    from datetime import datetime
    timestamp = (datetime.now()).strftime('%Y%b%d_%H%M').upper()
    return timestamp

def create_timestamp_uid():
    # generates UUID for the batch setup
    import uuid
    from datetime import datetime
    
    uid = ((str(uuid.uuid1()).replace('-', '')).upper())
    timestamp = (datetime.now()).strftime('%Y%b%d_%H%M').upper()
    return timestamp + '_' + uid[:3]

def scan_folders(dir, ext_list):    # dir: str, ext: list
    subfolders, files = [], []

    if not os.path.isdir(dir):
        return subfolders, files

    for f in os.scandir(dir):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[-1].lower() in ext_list:
                files.append(f.path)

    for dir in sorted(list(subfolders)):
        sf, f = scan_folders(dir, ext_list)
        subfolders.extend(sf)
        files.extend(f)

    return sorted(subfolders), sorted(files)

def sanitize_name(name):
    if name is None:
        return None

    import re
    name = name.strip()
    exp = re.compile(u'[^\w\.-]', re.UNICODE)
    result = exp.sub('_', name)
    return re.sub('_\_+', '_', result)

def create_uid():
    import uuid
    uid = ((str(uuid.uuid1()).replace('-', '')).upper())
    return uid[:3]

def remote_listdir(path, user, host):
    cmd_ls_remote = [
            'ssh',
            user + '@' + host,
            'ls', '-1',
            path
            ]

    cmd_ls_remote_result = subprocess.run(cmd_ls_remote, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmd_ls_remote_result = cmd_ls_remote_result.stdout.decode()
    return cmd_ls_remote_result.split('\n')[:-1]

def remote_rm(path, user, host):
    cmd_rm_remote = [
            'ssh',
            user + '@' + host,
            'rm', '-rf',
            path
            ]
    cmd_ls_remote_result = subprocess.run(cmd_rm_remote, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmd_ls_remote_result = cmd_ls_remote_result.stdout.decode()
    return cmd_ls_remote_result

def rsync(user, host, remote_path, local_path, verbose = False):

    src_path = user + '@' + host + ':' + remote_path
    dest_path = local_path

    if dest_path.endswith(os.path.sep):
        if not os.path.isdir(dest_path):
            try:
                os.makedirs(dest_path)
            except Exception as e:
                pprint (e)

    rsync_path = '/usr/bin/rsync'
    if verbose:
        cmd_rsync = rsync_path + ' -rLptvh ' + src_path + ' ' + dest_path
    else:
        cmd_rsync = rsync_path + ' -rLpt ' + src_path + ' ' + dest_path
    os.system(cmd_rsync)
    return dest_path