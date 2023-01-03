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

    kitsu_data = dict()

    write_kitsu_data_thread = threading.Thread(target=update_app_data_kitsu, args=(app_data, kitsu_data, log))
    write_kitsu_data_thread.daemon = True
    write_kitsu_data_thread.start()

    get_kitsu_projects_thread = threading.Thread(target=get_kitsu_metadata, args=(app_data, kitsu_data, log))
    get_kitsu_projects_thread.daemon = True
    get_kitsu_projects_thread.start()

    while True:
        try:
            time.sleep(4)
        except KeyboardInterrupt:
            return
        except Exception as e:
            log.error('exception in "sequence_sync": %s' % pformat(e))
            time.sleep(4)

def update_app_data_kitsu(app_data, kitsu_data, log):
    while True:
        try:
            app_data['kitsu'].update(kitsu_data)
            time.sleep(0.1)
        except KeyboardInterrupt:
            return
        except Exception as e:
            log.error('exception in "write_kitsu_data": %s' % pformat(e))
            time.sleep(4)

def get_kitsu_metadata(app_data, kitsu_data, log):
    while True:
        try:
            config = app_data.get('config').copy()
            try:
                timeout = config['robot']['timeout']
            except:
                timeout = 4
            config_gazu = config.get('gazu')
            host = config_gazu.get('host')
            name = config_gazu.get('name')
            password = config_gazu.get('password')
            gazu_client = gazu.client.create_client(host)
            gazu.log_in(name, password, client = gazu_client)

            time.sleep(timeout)
            gazu.log_out(client=gazu_client)
        except KeyboardInterrupt:
            return
        except Exception as e:
            log.error('exception in "write_kitsu_data": %s' % pformat(e))
            time.sleep(4)
