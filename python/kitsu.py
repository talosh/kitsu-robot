import os
import sys
import time
import threading
from .config import get_config_data
from pprint import pprint, pformat

import gazu

from .util import RobotLog

def kitsu_loop(app_data):
    log = RobotLog(app_data['config'], filename = 'kitsu.log')

    pprint (app_data.copy())

    kitsu_data = dict()

    while True:
        try:
            config = app_data.get('config').copy()
            config_gazu = config.get('gazu')
            host = config_gazu.get('host')
            name = config_gazu.get('name')
            password = config_gazu.get('password')

            pprint (config_gazu)

            time.sleep(4)
        except KeyboardInterrupt:
            return
        except Exception as e:
            log.error('exception in "sequence_sync": %s' % pformat(e))
            time.sleep(4)

def write_kitsu_data(app_data, kitsu_data, log):
    while True:
        try:
            app_data['kitsu']  = kitsu_data
            time.sleep(0.1)
        except KeyboardInterrupt:
            return
        except Exception as e:
            log.error('exception in "write_kitsu_data": %s' % pformat(e))
            time.sleep(4)