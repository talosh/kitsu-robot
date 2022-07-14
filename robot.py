from datetime import date, datetime, timedelta
import os
import sys
import time
import threading
import atexit
import inspect
import re
import subprocess
import uuid

import gazu

from pprint import pprint, pformat

from python.tailon import tailon

DEBUG=True

__version__ = 'v0.0.1'

if __name__ == "__main__":
    
    '''
    print ('... starting robot ...')
    print ('robot says:')
    print ('----')
    if os.path.isfile('/usr/games/fortune'):
        os.system('/usr/games/fortune')
    else:
        print ("Let's smash it!")
    print ('----')

    shotgun_api3.shotgun. NO_SSL_VALIDATION = True

    sg_credentials = {}
    sg_credentials['site'] = os.environ.get('SG_SITE')
    sg_credentials['script_name'] = os.environ.get('SG_SCRIPT_NAME')
    sg_credentials['api_key'] = os.environ.get('SG_SCRIPT_KEY')

    if None in sg_credentials.values():
        print ('Shotgrid credentials not set')
        pprint (sg_credentials)

    config = {}
    config['server_user'] = os.environ.get('SERVER_USER')
    config['server_host'] = os.environ.get('SERVER_HOST')
    if None in sg_credentials.values():
        print ('Server is not set')
        pprint (config)

    config['sg_credentials'] = sg_credentials
    config['temp_folder'] = os.environ.get('TMP_DIR') if os.environ.get('TMP_DIR') else '/var/tmp'
    config['rsync_path'] = '/usr/bin/rsync'
    config['natron_scripts'] = os.path.join(os.path.dirname(__file__), 'resources', 'natron')
    config['natron_binary'] = '/opt/Natron/bin/NatronRenderer'
    config['app_location'] = os.path.abspath(os.path.dirname(__file__))
    config['projects_config'] = os.environ.get('PROJECTS_CONFIG', os.path.join(os.path.dirname(__file__), 'resources', 'projects'))
    

    print ('cleaning temp folder: %s' % config.get('temp_folder'))
    clean_temp_cmd = 'rm -rf ' + config.get('temp_folder')
    if clean_temp_cmd.endswith(os.path.sep):
        clean_temp_cmd += '*'
    else:
        clean_temp_cmd += os.path.sep + '*'
    os.system(clean_temp_cmd)

    print ('version: %s' % __version__)

    sg_cache = None
    while True:
        try:
            sg_cache = sgCache(
                sg_credentials['site'],
                sg_credentials['script_name'],
                sg_credentials['api_key']
                )
        except Exception as e:
            print ('Unable to connect, retrying...')
            pprint (e)
            if sg_cache:
                del (sg_cache)
            time.sleep(8)
        else:
            break

    print ('Waiting for tasks ...')

    weblog_thread = threading.Thread(target=tailon, args=(sg_cache, config))
    weblog_thread.daemon = True
    weblog_thread.start()

    review_thread = threading.Thread(target=review_robot, args=(sg_cache, config))
    review_thread.daemon = True
    review_thread.start()

    delivery_thread = threading.Thread(target=delivery_robot, args=(sg_cache, config))
    delivery_thread.daemon = True
    delivery_thread.start()
    '''

    config = {}

    weblog_thread = threading.Thread(target=tailon, args=(config, ))
    weblog_thread.daemon = True
    weblog_thread.start()

    gazu.set_host("http://192.168.15.99/api")
    gazu.log_in("admin@dirtylooks.co.uk", "dirtylooks")

    while True:
        try:
            # print ('[' + datetime.now().strftime("%Y%m%d %H:%M") + ']\n' + 'Hello from Kitsu-Robot' + '\n')
            projects = gazu.project.all_open_projects()
            for project in projects:
                print ('name: %s' % project.get('name'))
                descriptors_api_path = '/data/projects/' + project.get('id') + '/metadata-descriptors'
                project_descriptor_data = gazu.client.get(descriptors_api_path)
                project_descriptor_names = [x['name'] for x in project_descriptor_data]
                pprint (project_descriptor_names)
                pprint (project_descriptor_data)
                if 'test' not in project_descriptor_names:
                    data = {
                        'name': 'test',
                        'choices': [],
                        'for_client': False,
                        'entity_type': 'Shot',
                        'departments': []
                    }
                    gazu.client.post(descriptors_api_path, data)
            # data = gazu.client.fetch_all("shots")
            # pprint (data)
            # pprint (dir(gazu))
            time.sleep(4)
        except KeyboardInterrupt:
            sys.exit()
