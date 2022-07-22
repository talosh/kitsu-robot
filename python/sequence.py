import os
import sys
import time
from pprint import pprint, pformat

def sequence_sync(config):
    flapi_module_path = config.get('flapi_module_path')
    log.verbose('importing flapi from %s' % flapi_module_path)
