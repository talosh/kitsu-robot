from datetime import date, datetime, timedelta
import os
import sys
import time
import multiprocessing
import threading
import atexit
import inspect
import re
import subprocess
import uuid
from copy import deepcopy
from pprint import pprint, pformat

from python.config import get_config_data
from python.config import config_reader
from python.tailon import tailon
from python.metadata_fields import set_metadata_fields
from python.sequence import sequence_sync
from python.util import RobotLog

APP_NAME = 'KitsuRobot'
VERBOSE=True
DEBUG=True

__version__ = 'v0.0.5 dev 001'

if __name__ == "__main__":

    # set main data template using proxy objects
    manager = multiprocessing.Manager()
    app_data = manager.dict()
    app_data['config'] = manager.dict()
    app_data['baselight'] = manager.dict()
    app_data['kitsu'] = manager.dict()

    app_location = os.path.dirname(os.path.abspath(__file__))
    # config_folder_path = os.path.join(app_location, 'config')

    # set some defaut values in config
    app_data['config']['app_location'] = app_location
    app_data['config']['app_name'] = APP_NAME
    app_data['config']['verbose'] = VERBOSE
    app_data['config']['debug'] = DEBUG
    app_data['config']['version'] = ('version %s' % __version__)
    app_data['config']['log_folder'] = os.path.join(app_location, 'log')
    app_data['config']['temp_folder'] = os.path.join(app_location, 'tmp')
    app_data['config']['remote_temp_folder'] = '/var/tmp'

    # read config on startup so we can safely start other processes and threads
    config_folder_path = os.path.join(app_location, 'config')
    current_config = get_config_data(config_folder_path)
    for config_key in current_config.keys():
        app_data['config'][config_key] = current_config[config_key]

    # print ('reading config files from ' + config_folder_path)
    
    # app_config = get_config_data(config_folder_path)
    # for app_config_key in app_config.keys():
    #    app_data['config'][app_config_key] = app_config[app_config_key]

    # pprint (app_data['config'].copy())
    # sys.exit()

    active_threads = []

    config_reader_therad = threading.Thread(target=config_reader, args=(app_data, ))
    config_reader_therad.daemon = True
    config_reader_therad.start()

    tailon_thread = threading.Thread(target=tailon, args=(app_data, ))
    tailon_thread.daemon = True
    tailon_thread.start()

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
    '''

    while True:
        try:
            config = app_data['config'].copy()
            pprint (config.get('robot'))
            time.sleep(4)
        except KeyboardInterrupt:
            sys.exit()