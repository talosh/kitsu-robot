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

    kitsu_data = {}

    write_kitsu_data_thread = threading.Thread(target=write_kitsu_data, args=(app_data, kitsu_data, log))
    write_kitsu_data_thread.daemon = True
    write_kitsu_data_thread.start()

    while True:
        try:
            config = app_data.get('config').copy()
            config_gazu = config.get('gazu')
            host = config_gazu.get('host')
            name = config_gazu.get('name')
            password = config_gazu.get('password')

            kitsu_data = config_gazu.copy()
            time.sleep(4)
        except KeyboardInterrupt:
            return
        except Exception as e:
            log.error('exception in "sequence_sync": %s' % pformat(e))
            time.sleep(4)

def write_kitsu_data(app_data, kitsu_data, log):
    while True:
        try:
            pprint (kitsu_data)
            for key in kitsu_data.keys():
                app_data['kitsu'][key] = kitsu_data[key]
            time.sleep(0.1)
        except KeyboardInterrupt:
            return
        except Exception as e:
            log.error('exception in "write_kitsu_data": %s' % pformat(e))
            time.sleep(4)