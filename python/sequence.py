import os
import sys
import time
from pprint import pprint, pformat

def sequence_sync(config):
    log = config.get('log')

    import gazu
    config_gazu = config.get('gazu')
    host = config_gazu.get('host')
    name = config_gazu.get('name')
    password = config_gazu.get('password')
    gazu.set_host(host)
    gazu.log_in(name, password)

    while True:
        try:
            projects = gazu.project.all_open_projects()
            for project in projects:
                sequences_api_path = '/data/projects/' + project.get('id') + '/sequences'
                project_sequences = gazu.client.get(sequences_api_path)
                for project_sequence in project_sequences:
                    data = project_sequence.get('data')
                    if isinstance(data, dict):
                        if 'blpath' in data.keys():
                            pprint (data)
            time.sleep(4)
        except KeyboardInterrupt:
            return

'''

    flapi_module_path = config.get('flapi_module_path')
    log.verbose('importing flapi from %s' % flapi_module_path)

    try:
        if sys.path[0] != flapi_module_path:
            sys.path.insert(0, flapi_module_path)
        import flapi
    except Exception as e:
        log.error('unable to import filmlight api python module from: %s' % flapi_module_path)
        log.error(e)

'''