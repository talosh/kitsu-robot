import os
import sys
import datetime
import subprocess
import traceback
import time
from .common import log

from pprint import pprint, pformat

def tailon(config):
    while True:
        try:
            cmd_hostname_result = []
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
                    if cmd_ipconfig_result:
                        cmd_hostname_result.append(cmd_ipconfig_result)

                pprint (cmd_hostname_result)
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
                bind_string += host_ip + ':' + config.get('WEBLOG_PORT', '8088') + ','
            if bind_string.endswith(','):
                bind_string = bind_string[:-1]

            tailon_location = config.get('TAILON_BINARY', '/opt/kitsu-robot/robotenv/bin/tailon')
            logfile_location = config.get('LOGFILE', '/opt/kitsu-robot/log/robot.log')
            if os.path.isfile(tailon_location):
                cmd_tailon = [
                    tailon_location,
                    '-b',
                    bind_string,
                    logfile_location
                    ]

                subprocess.run(cmd_tailon, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        except KeyboardInterrupt:
            sys.exit()

        except Exception as e:
            message += 'Exception at ' + datetime.now().strftime("%Y-%m-%d %H:%M") + ': ' + pformat(e)
            log (message)
            log (traceback.format_exc())
            time.sleep(1)

