import os
import sys
import time

from .util import remote_listdir
from .util import remote_rm
from .util import rsync

from .config import get_config_data

from pprint import pprint, pformat


def baselight_process(app_data):
    log = app_data['config'].get('log')

    while True:
        try:
            time.sleep(4)
        except KeyboardInterrupt:
            return
        except Exception as e:
            log.error('exception in "sequence_sync": %s' % pformat(e))
            time.sleep(4)
