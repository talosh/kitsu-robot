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
            baselight_linked_sequences = []
            projects = gazu.project.all_open_projects()
            for project in projects:
                sequences_api_path = '/data/projects/' + project.get('id') + '/sequences'
                project_sequences = gazu.client.get(sequences_api_path)
                for project_sequence in project_sequences:
                    data = project_sequence.get('data')
                    if isinstance(data, dict):
                        if 'blpath' in data.keys():
                            baselight_linked_sequences.append(project_sequence)
            for baselight_linked_sequence in baselight_linked_sequences:
                link_baselight_sequence(config, baselight_linked_sequence)
            time.sleep(4)
        except KeyboardInterrupt:
            return

def link_baselight_sequence(config, baselight_linked_sequence):
    log = config.get('log')
    data = baselight_linked_sequence.get('data')
    if not isinstance(data, dict):
        log.info('no baselight path found in sequence "%s"' % pformat(baselight_linked_sequence))
        return
    blpath = data.get('blpath')
    if not blpath:
        log.info('no baselight path found in sequence "%s"' % pformat(baselight_linked_sequence))
        return
    blpath_components = blpath.split(':')
    flapi_hosts = config.get('flapi_hosts')
    if not flapi_hosts:
        log.info('no flapi hosts defined in configuration')
        return
    flapi_hosts = {x['flapi_hostname']:x for x in flapi_hosts}
    if blpath_components[0] not in flapi_hosts.keys():
        log.info('host "%s" is not defined in flapi_hosts config file' % blpath_components[0])
        return
    baselight_shots = get_baselight_scene_shots(config, blpath)

def get_baselight_scene_shots(config, blpath):
    log = config.get('log')
    flapi_module_path = config.get('flapi_module_path')
    log.verbose('importing flapi from %s' % flapi_module_path)
    try:
        if sys.path[0] != flapi_module_path:
            sys.path.insert(0, flapi_module_path)
        import flapi
    except Exception as e:
        log.error('unable to import filmlight api python module from: %s' % flapi_module_path)
        log.error(e)

    blpath_components = blpath.split(':')
    flapi_hosts = config.get('flapi_hosts')
    flapi_hosts = {x['flapi_hostname']:x for x in flapi_hosts}
    flapi_host = flapi_hosts.get(blpath_components[0])
    flapi_hostname = flapi_host.get('flapi_hostname')
    flapi_user = flapi_host.get('flapi_user')
    flapi_token = flapi_host.get('flapi_tokenn')    

    if not all([flapi_hostname, flapi_user, flapi_token]):
        log.info('missing data in flapi host configuration:\n %s' % pformat(flapi_host))
        return []

    # log.verbose('opening flapi connection to %s' % flapi_hostname)


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