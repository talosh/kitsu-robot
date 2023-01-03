import os
import sys
import time
from .config import get_config_data
from pprint import pprint, pformat

import gazu

from .util import RobotLog

def kitsu_loop(app_data):
    log = RobotLog(app_data['config'], filename = 'kitsu.log')

    pprint (app_data['config'].copy())

    while True:
        try:
            time.sleep(4)
        except KeyboardInterrupt:
            return
        except Exception as e:
            log.error('exception in "sequence_sync": %s' % pformat(e))
            time.sleep(4)
