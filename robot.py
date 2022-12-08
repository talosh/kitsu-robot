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
from pprint import pprint, pformat

from python.config import get_config_data
from python.tailon import tailon
from python.metadata_fields import set_metadata_fields
from python.sequence import sequence_sync
from python.util import Log

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

    # read config and populate default values
    app_location = os.path.dirname(os.path.abspath(__file__))
    config_folder_path = os.path.join(app_location, 'config')
    print ('reading config files from ' + config_folder_path)
    app_config = get_config_data(config_folder_path)
    app_config['app_name'] = APP_NAME
    app_config['verbose'] = VERBOSE
    app_config['debug'] = DEBUG
    app_config['log'] = Log(app_config)
    app_config['log'].info('version %s' % __version__)
    app_config['temp_folder'] = os.path.join(app_location, 'tmp')
    app_config['remote_temp_folder'] = '/var/tmp'
    for app_config_key in app_config.keys():
        app_data['config'][app_config_key] = app_config[app_config_key]

    pprint (app_data)
    sys.exit()

    weblog_thread = threading.Thread(target=tailon, args=(app_config, ))
    weblog_thread.daemon = True
    weblog_thread.start()

    metadata_thread = threading.Thread(target=set_metadata_fields, args=(app_config, ))
    metadata_thread.daemon = True
    metadata_thread.start()

    sequence_sync_thread = threading.Thread(target=sequence_sync, args=(app_config, ))
    sequence_sync_thread.daemon = True
    sequence_sync_thread.start()
    

    while True:
        try:
            time.sleep(4)
        except KeyboardInterrupt:
            sys.exit()

"wookie:dlj0356_mr_malcolms_list:grade:reel_01_v*"