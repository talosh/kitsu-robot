import os
import sys
import datetime
import subprocess
import traceback
import time
from copy import deepcopy
from .common import log

from pprint import pprint, pformat

def tailon(app_data):
    config = {}
    while True:
        app_config = deepcopy(app_data['config'])
        log_folder = app_config.get('log_folder', '/opt/kitsu-robot/log/robot.log')
        robot_config = app_config.get('robot')
        if robot_config:
            tailon_config = robot_config.get('tailon')
        if tailon_config:
            config = deepcopy(tailon_config)
        try:
            cmd_hostname_result = ['127.0.0.1']
            if config.get('bind_all'):
                if sys.platform == 'darwin':
                    interface_names = []
                    cmd_networksetup = [
                        'networksetup',
                        '-listallhardwareports'
                    ]
                    cmd_networksetup_result = subprocess.run(cmd_networksetup, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    cmd_networksetup_result = cmd_networksetup_result.stdout.decode()
                    for line in cmd_networksetup_result.splitlines():
                        if line.startswith('Device'):
                            interface_names.append(line.rsplit(': ')[1])

                    for ifname in interface_names:
                        cmd_ipconfig = [
                            'ipconfig',
                            'getifaddr',
                            ifname
                        ]
                        cmd_ipconfig_result = subprocess.run(cmd_ipconfig, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        cmd_ipconfig_result = cmd_ipconfig_result.stdout.decode()
                        cmd_ipconfig_result = cmd_ipconfig_result.replace('\n', '')
                        if cmd_ipconfig_result:
                            cmd_hostname_result.append(cmd_ipconfig_result)
                else:
                    cmd_hostname = [
                            'hostname',
                            '-I'
                            ]

                    cmd_hostname_result = subprocess.run(cmd_hostname, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    cmd_hostname_result = cmd_hostname_result.stdout.decode()
                    cmd_hostname_result = cmd_hostname_result.replace('\n', '')
                    cmd_hostname_result = cmd_hostname_result.split(' ')

            bind_string = ''
            for host_ip in cmd_hostname_result:
                if not host_ip:
                    continue
                bind_string += host_ip + ':' + str(config.get('port', '8088')) + ','
            if bind_string.endswith(','):
                bind_string = bind_string[:-1]

            tailon_location = config.get('tailon_binary', '/opt/kitsu-robot/robotenv/bin/tailon')
            logfile_string = os.path.join(log_folder, '*.log')
            relative_root_string = '--relative-root ' + config.get('relative_root', '/')
            if os.path.isfile(tailon_location):
                cmd_tailon = [
                    tailon_location,
                    relative_root_string,
                    '-b',
                    bind_string,
                    logfile_string
                    ]
                
                pprint (cmd_tailon)
                subprocess.run(cmd_tailon, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        except KeyboardInterrupt:
            sys.exit()

        except Exception as e:
            message = 'Exception at ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + ': ' + pformat(e)
            log (message)
            log (traceback.format_exc())
            time.sleep(1)

