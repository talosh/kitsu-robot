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
from pprint import pprint, pformat

from python.config import get_config_data
from python.tailon import tailon
from python.metadata_fields import set_metadata_fields
from python.sequence import sequence_sync

DEBUG=True

__version__ = 'v0.0.2'

if __name__ == "__main__":
    app_location = os.path.dirname(os.path.abspath(__file__))
    config_folder_path = os.path.join(app_location, 'config')
    app_config = get_config_data(config_folder_path)

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

    weblog_thread = threading.Thread(target=tailon, args=(app_config, ))
    weblog_thread.daemon = True
    weblog_thread.start()

    metadata_thread = threading.Thread(target=set_metadata_fields, args=(app_config, ))
    metadata_thread.daemon = True
    metadata_thread.start()

    sequence_sync_thread = threading.Thread(target=sequence_sync, args=(app_config, ))
    sequence_sync_thread.daemon = True
    sequence_sync_thread.start()
    
    import gazu
    config = app_config
    config_gazu = config.get('gazu')
    host = config_gazu.get('host')
    name = config_gazu.get('name')
    password = config_gazu.get('password')
    gazu.set_host(host)
    gazu.log_in(name, password)

    while True:
        try:
            projects = gazu.project.all_open_projects()
            for project in projects:
                sequences_api_path = '/data/projects/' + project.get('id') + '/sequences'
                project_sequences_data = gazu.client.get(sequences_api_path)
                pprint (project_sequences_data)
            time.sleep(4)
        except KeyboardInterrupt:
            sys.exit()

"wookie:dlj0356_mr_malcolms_list:grade:reel_01_v*"