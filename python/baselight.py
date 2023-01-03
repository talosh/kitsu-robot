import os
import sys
import time
import threading

from .util import remote_listdir
from .util import remote_rm
from .util import rsync

from .config import get_config_data
from .util import RobotLog

from pprint import pprint, pformat


def baselight_loop(app_data):
    log = RobotLog(app_data['config'], filename = 'baselight.log')

    while True:
        try:
            kitsu_data = app_data.get('kitsu')
            pprint (kitsu_data)
            time.sleep(4)
        except KeyboardInterrupt:
            return
        except Exception as e:
            log.error('exception in "sequence_sync": %s' % pformat(e))
            time.sleep(4)
