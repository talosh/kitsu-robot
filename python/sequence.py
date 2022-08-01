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

    import gazu
    config_gazu = config.get('gazu')
    host = config_gazu.get('host')
    name = config_gazu.get('name')
    password = config_gazu.get('password')
    gazu.set_host(host)
    gazu.log_in(name, password)

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

    project_dict = gazu.project.get_project(baselight_linked_sequence.get('project_id'))
    shots = gazu.shot.all_shots_for_sequence(baselight_linked_sequence)

    for baselight_shot in baselight_shots:
        shot_md = baselight_shot.get('shot_md')
        if not shot_md:
            continue
        rectc = shot_md.get('rectc')
        if not rectc:
            continue
        new_shot = gazu.shot.new_shot(
            project_dict, 
            baselight_linked_sequence, 
            str(rectc[0])
        )

        pprint (new_shot)

        # pprint(str(rectc[0]))        
    sys.exit()

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

    conn = fl_connect(config, flapi, flapi_host)
    if not conn:
        return []

    scene_path = fl_get_scene_path(config, flapi, conn, blpath)
    if not scene_path:
        return []

    try:
        log.verbose('loading scene: %s' % scene_path)
        scene = conn.Scene.open_scene( scene_path, { flapi.OPENFLAG_READ_ONLY } )
    except flapi.FLAPIException as ex:
        log.error( "Error loading scene: %s" % ex )
        return []

    baselight_shots = []

    nshots = scene.get_num_shots()
    log.verbose( "Found %d shot(s)" % nshots )

    md_keys = set()
    mddefns = scene.get_metadata_definitions()
    for mdfn in mddefns:
        md_keys.add(mdfn.Key)

    if nshots > 0:
        shots = scene.get_shot_ids(0, nshots)
        for shot_ix, shot_inf in enumerate(shots):
            # log.verbose("Shot %d:" % shot_ix)
            shot = scene.get_shot(shot_inf.ShotId)
            shot_md = shot.get_metadata(md_keys)
            # shot_md = shot.get_metadata_strings(md_keys)
            mark_ids = shot.get_mark_ids()
            categories = shot.get_categories()

            baselight_shots.append(
                {
                    'shot_id': shot_ix,
                    'shot_md': shot_md,
                    'mark_ids': mark_ids,
                    'categories': categories
                }
            )

            shot.release()

    '''
    test_tc = conn.Utilities.timecode_from_string('01:00:00:00')
    pprint (test_tc)
    pprint (str(test_tc))
    pprint (dir(test_tc))
    '''

    '''
    # show avaliable keys and their types
    mddefns = scene.get_metadata_definitions()
    for mdfn in mddefns:
        print ('%15s: %s, %s' % (mdfn.Key, mdfn.Name, mdfn.Type))
    cat_keys = scene.get_strip_categories()
    pprint (cat_keys)
    '''

    scene.close_scene()
    scene.release()
    
    fl_disconnect(config, flapi, flapi_host, conn)

    return baselight_shots

def fl_get_scene_path(config, flapi, conn, blpath):
    log = config.get('log')

    blpath_components = blpath.split(':')
    flapi_hosts = config.get('flapi_hosts')
    flapi_hosts = {x['flapi_hostname']:x for x in flapi_hosts}
    flapi_host = flapi_hosts.get(blpath_components[0])
    bl_jobname = blpath_components[1]
    bl_scene_name = blpath_components[-1]
    bl_scene_path = ':'.join(blpath_components[2:])
    bl_scenes_folder = ''.join(blpath_components[2:-1])
    flapi_hostname = flapi_host.get('flapi_hostname')

    if '*' in bl_scene_name:
        # find the most recent scene
        import re
        log.verbose('finding most recent baselight scene for pattern: %s' % blpath)
        existing_scenes = conn.JobManager.get_scenes(flapi_hostname, bl_jobname, bl_scenes_folder)
        matched_scenes = []
        for scene_name in existing_scenes:
            if re.findall(bl_scene_name, scene_name):
                matched_scenes.append(scene_name)

        if not matched_scenes:
            log.verbose('no matching scenes found for: %s' % blpath)
            return None
        else:
            # TODO
            # this to be changed to actually checking the most recently modified scene
            # instead of just plain alphabetical sorting and taking the last one

            scene_name = sorted(matched_scenes)[-1]
            log.verbose('Alphabetically recent scene: %s' % scene_name)
            bl_scene_path = bl_scenes_folder + ':' + scene_name
            blpath = flapi_hostname + ':' + bl_jobname + ':' + bl_scene_path

    else:
        # we have full scene path and need to check if scene exists

        log.verbose('checking baselight scene: %s' % blpath)

        if not conn.JobManager.scene_exists(flapi_hostname, bl_jobname, bl_scene_path):
            log.verbose('baselight scene %s does not exist' % blpath)
            return None
        else:
            log.verbose('baselight scene %s exists' % blpath)

    
    try:
        scene_path = conn.Scene.parse_path(blpath)
    except flapi.FLAPIException as ex:
        log.verbose('Can not parse scene: %s' % blpath)
        return None

    return scene_path


def fl_connect(config, flapi, flapi_host):
    log = config.get('log')
    flapi_hostname = flapi_host.get('flapi_hostname')
    flapi_user = flapi_host.get('flapi_user')
    flapi_token = flapi_host.get('flapi_token')

    if not all([flapi_hostname, flapi_user, flapi_token]):
        log.info('missing data in flapi host configuration:\n %s' % pformat(flapi_host))
        return []

    log.verbose('opening flapi connection to %s' % flapi_hostname)
    log.debug('flapi user: %s' % flapi_user)
    log.debug('flapi token: %s' % flapi_token)

    log.verbose('opening flapi connection to %s' % flapi_hostname)
    try:
        conn = flapi.Connection(
            flapi_hostname,
            username=flapi_user,
            token=flapi_token
        )
        conn.connect()
    except flapi.FLAPIException as e:
        log.error('Unable to open flapi connection to %s' % flapi_hostname)
        log.error(e)
        conn = None
    except Exception as e:
        log.error('Unable to open flapi connection to %s' % flapi_hostname)
        log.error(e)
        conn = None
    log.verbose('connected to %s' % flapi_hostname)
    return conn

def fl_disconnect(config, flapi, flapi_host, conn):
    log = config.get('log')
    flapi_hostname = flapi_host.get('flapi_hostname')
    flapi_user = flapi_host.get('flapi_user')
    flapi_token = flapi_host.get('flapi_token')

    log.verbose('closing flapi connection to %s' % flapi_hostname)
    try:
        conn.close()
    except flapi.FLAPIException as e:
        log.error('Unable to close flapi connection to %s' % flapi_hostname)
        log.error(e)
        conn = None
    except Exception as e:
        log.error('Unable to close flapi connection to %s' % flapi_hostname)
        log.error(e)
        conn = None
    log.verbose('connection to %s closed' % flapi_hostname)

