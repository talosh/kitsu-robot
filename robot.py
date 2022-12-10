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
from python.baselight import baselight_process

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

    # set some default values in config
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

    log = RobotLog(app_data['config'], filename = 'robot.log')
    # print ('reading config files from ' + config_folder_path)
    
    # app_config = get_config_data(config_folder_path)
    # for app_config_key in app_config.keys():
    #    app_data['config'][app_config_key] = app_config[app_config_key]

    # pprint (app_data['config'].copy())
    # sys.exit()

    processes = []
    log.debug ('creating config reader thread')
    config_reader_thread = threading.Thread(target=config_reader, args=(app_data, ))
    config_reader_thread.daemon = True
    config_reader_thread.start()

    # TailOn starts as a separate process
    # log.debug ('creating tailon thread')
    # tailon_thread = threading.Thread(target=tailon, args=(app_data, ))
    # tailon_thread.daemon = True
    # tailon_thread.start()

    bl_process = multiprocessing.Process(
        target=baselight_process,
        name = 'Baselight Flapi Process',
        args=(app_data, )
        )
    processes.append(bl_process)
    log.debug ('Starting Baselight Flapi Process')
    bl_process.start()


    # compatibility with old code
    config = {}
    for key in app_data['config'].keys():
        config[key] = app_data['config'][key]
    config['log'] = log

    metadata_thread = threading.Thread(target=set_metadata_fields, args=(config, ))
    metadata_thread.daemon = True
    metadata_thread.start()

    '''
    sequence_sync_thread = threading.Thread(target=sequence_sync, args=(config, ))
    sequence_sync_thread.daemon = True
    sequence_sync_thread.start()
    '''

    while True:
        try:
            try:
                timeout = app_data['config']['robot']['timeout']
            except:
                timeout = 4
            time.sleep(timeout)
        except KeyboardInterrupt:
            for p in processes:
                log('terminating %s' % p.name)
                p.terminate()
                p.join()
            sys.exit()