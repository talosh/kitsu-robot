import os
import sys
import time

from .util import remote_listdir
from .util import remote_rm
from .util import rsync

from pprint import pprint, pformat

def sequence_sync(config):
    log = config.get('log')

    import gazu

    while True:
        try:

            config_gazu = config.get('gazu')
            host = config_gazu.get('host')
            name = config_gazu.get('name')
            password = config_gazu.get('password')
            gazu.set_host(host)
            gazu.log_in(name, password)

            baselight_linked_sequences = []
            projects = gazu.project.all_open_projects()
            for project in projects:
                sequences_api_path = '/data/projects/' + project.get('id') + '/sequences'
                project_sequences = gazu.client.get(sequences_api_path)
                for project_sequence in project_sequences:
                    data = project_sequence.get('data')
                    if isinstance(data, dict):
                        if 'blpath' in data.keys():
                            blpath = data.get('blpath')
                            if blpath:
                                baselight_linked_sequences.append(project_sequence)
            for baselight_linked_sequence in baselight_linked_sequences:
                # collect common data queries
                blpath = resolve_blpath(config, baselight_linked_sequence)
                
                # debug filter block
                # if not 'dlj9001' in blpath:
                '''
                if not 'dlj0412_catching_dust' in blpath:
                    # pass
                    continue
                '''
                # end of debug filter block
                
                if not blpath:
                    continue
                baselight_linked_sequence['blpath'] = blpath
                baselight_shots = get_baselight_scene_shots(config, blpath)
                if not baselight_shots:
                    continue
                baselight_linked_sequence['baselight_shots'] = baselight_shots
                kitsu_uid_metadata_obj = check_or_add_kitsu_metadata_definition(config, blpath)
                baselight_linked_sequence['kitsu_uid_metadata_obj'] = kitsu_uid_metadata_obj
                kitsu_shots = gazu.shot.all_shots_for_sequence(baselight_linked_sequence)
                baselight_linked_sequence['kitsu_shots'] = kitsu_shots

                populate_kitsu_from_baselight_sequence(config, gazu, baselight_linked_sequence)
                # sync_shot_marks(config, gazu, baselight_linked_sequence)
                # sync_filenames_and_version_numbers(config, gazu, baselight_linked_sequence)
                
            time.sleep(4)
            gazu.log_out()
        except KeyboardInterrupt:
            return

def sync_filenames_and_version_numbers(config, gazu, baselight_linked_sequence):
    log = config.get('log')
    blpath = baselight_linked_sequence.get('blpath')
    baselight_shots = baselight_linked_sequence.get('baselight_shots')
    kitsu_uid_metadata_obj = baselight_linked_sequence.get('kitsu_uid_metadata_obj')
    kitsu_shots = baselight_linked_sequence.get('kitsu_shots')
    baselight_shots_by_kitsu_uid = {x['shot_md'].get(kitsu_uid_metadata_obj.Key):x for x in baselight_shots}

    flapi = import_flapi(config)
    flapi_host = resolve_flapi_host(config, blpath)
    conn = fl_connect(config, flapi, flapi_host)
    if not conn:
        return None
    scene_path = fl_get_scene_path(config, flapi, conn, blpath)
    if not scene_path:
        return None

    try:
        log.verbose('Opening scene: %s' % scene_path)
        scene = conn.Scene.open_scene( scene_path, { flapi.OPENFLAG_READ_ONLY } )
    except flapi.FLAPIException as ex:
        log.error( "Error opening scene: %s" % ex )
        return None

    baselight_shots = baselight_linked_sequence.get('baselight_shots')
    kitsu_shots = baselight_linked_sequence.get('kitsu_shots')
    kitsu_uid_metadata_obj = baselight_linked_sequence.get('kitsu_uid_metadata_obj')

    baselight_shots_by_kitsu_id = {}
    for baselight_shot in baselight_shots:
        shot_md = baselight_shot.get('shot_md')
        kitsu_uid = shot_md.get(kitsu_uid_metadata_obj.Key)
        baselight_shots_by_kitsu_id[kitsu_uid] = baselight_shot

    # pprint (baselight_shots_by_kitsu_id)

    for kitsu_shot in kitsu_shots:
        kitsu_id = kitsu_shot.get('id')
        if not kitsu_id:
            continue
        bl_shot = baselight_shots_by_kitsu_id.get(kitsu_id)
        pprint (bl_shot)
        continue
    
        k_shot = gazu.shot.get_shot()
        if not k_shot:

            continue
    
        bl_shot = baselight_shots_by_kitsu_id[kitsu_id]
        shot = scene.get_shot(shot_inf.ShotId)
        pprint (kitsu_shot)

    '''
    nshots = scene.get_num_shots()
    if nshots > 0:
        shots = scene.get_shot_ids(0, nshots)
        for shot_ix, shot_inf in enumerate(shots):
            print( "\r Syncing version for shot %d of %s" % (shot_ix + 1, nshots), end="" )
            # log.verbose("Shot %d:" % shot_ix)
            shot = scene.get_shot(shot_inf.ShotId)
            descriptor = shot.get_sequence_descriptor()
            filename = descriptor.get_name()

            kitsu_uid = shot_md.get(kitsu_uid_metadata_obj.Key)
            pprint (filename)
            shot.release()
    '''
    
    scene.close_scene()
    scene.release()


def sync_shot_marks(config, gazu, baselight_linked_sequence):
    import json
    log = config.get('log')
    blpath = baselight_linked_sequence.get('blpath')
    baselight_shots = baselight_linked_sequence.get('baselight_shots')
    kitsu_uid_metadata_obj = baselight_linked_sequence.get('kitsu_uid_metadata_obj')
    kitsu_shots = baselight_linked_sequence.get('kitsu_shots')
    baselight_shots_by_kitsu_uid = {x['shot_md'].get(kitsu_uid_metadata_obj.Key):x for x in baselight_shots}

    flapi = import_flapi(config)
    flapi_host = resolve_flapi_host(config, blpath)
    conn = fl_connect(config, flapi, flapi_host)
    if not conn:
        return None
    scene_path = fl_get_scene_path(config, flapi, conn, blpath)
    if not scene_path:
        return None

    try:
        log.verbose('Trying to open scene %s in read-write mode' % scene_path)
        scene = conn.Scene.open_scene( scene_path, {  flapi.OPENFLAG_DISCARD  })
    except flapi.FLAPIException as ex:
        log.error( "Error opening scene: %s" % ex )
        return

    mark_categories = scene.get_mark_categories()
    scene.start_delta('Add marks')

    for kitsu_shot in kitsu_shots:
        data = kitsu_shot.get('data')
        if not data:
            continue
        locator_string = data.get('01_locator')
        if not locator_string:
            continue
        if not (locator_string.startswith('[') and locator_string.endswith(']')):
            continue
        try:
            locator = json.loads(locator_string)
        except:
            return


        baselight_shot = baselight_shots_by_kitsu_uid.get(kitsu_shot['id'])
        if not baselight_shot:
            continue
        shot = scene.get_shot(baselight_shot['shot_id'])
        start_frame = shot.get_start_frame()
        src_start_frame = shot.get_src_start_frame()
        mark_ids = shot.get_mark_ids()
        existing_marks = []
        if len(mark_ids) > 0:
            for ix,m in enumerate(mark_ids):
                mark = shot.get_mark(m)
                print( "%20d: Frame %d Type '%s' Message '%s'" % (
                        ix,
                        mark.get_record_frame(),
                        mark.get_category(),
                        mark.get_note_text()
                    )
                )
                existing_marks.append(
                    pformat({
                        'type': mark.get_category(),
                        'frame': mark.get_record_frame(),
                        'label': mark.get_note_text()
                    })
                )
                mark.release()
                # shot.delete_mark(m)

        for new_mark_info in locator:
            new_mark = {
                'type': new_mark_info.get('type', mark_categories[0]),
                'frame': start_frame + new_mark_info.get('frame', 0),
                'label': new_mark_info.get('label', '')
            }

            if pformat(new_mark) not in existing_marks:
                shot.add_mark(
                    (src_start_frame - start_frame) + new_mark.get('frame', 0), 
                    new_mark.get('type', mark_categories[0]), 
                    new_mark.get('label', ''))
            else:
                print ('mark exists')
                pprint (new_mark)
        shot.release()

    scene.end_delta()
    scene.save_scene()
    scene.close_scene()
    scene.release()

    fl_disconnect(config, flapi, flapi_host, conn)
    return


def populate_kitsu_from_baselight_sequence(config, gazu, baselight_linked_sequence):
    log = config.get('log')

    blpath = baselight_linked_sequence.get('blpath')

    kitsu_uid_metadata_obj = baselight_linked_sequence.get('kitsu_uid_metadata_obj')
    if not kitsu_uid_metadata_obj:
        return
    baselight_shots = baselight_linked_sequence.get('baselight_shots')
    project_dict = gazu.project.get_project(baselight_linked_sequence.get('project_id'))
    kitsu_shots = baselight_linked_sequence.get('kitsu_shots')

    kitsu_shot_uids = set()
    for kitsu_shot in kitsu_shots:
        kitsu_shot_uids.add(kitsu_shot.get('id'))

    new_shots = []
        
    for baselight_shot in baselight_shots:
        shot_md = baselight_shot.get('shot_md')
        if not shot_md:
            continue
        kitsu_uid = shot_md.get(kitsu_uid_metadata_obj.Key)
        if kitsu_uid in kitsu_shot_uids:

            new_data = {}
            bl_shot_data = build_kitsu_shot_data(config, baselight_shot)
            kitsu_shot = gazu.shot.get_shot(kitsu_uid)
            kitsu_shot_data = kitsu_shot.get('data', dict())

            for data_key in bl_shot_data.keys():
                if kitsu_shot_data.get(data_key):
                    continue
                else:
                    new_data[data_key] = bl_shot_data.get(data_key)

            if not new_data:
                continue
            
            log.info('updating shot: %s' % kitsu_shot.get('name'))
            gazu.shot.update_shot(kitsu_shot, new_data)
            pprint (new_data)

        new_shots.append(baselight_shot)

    # try to open baselight scene and fill the shots back in with kitsu-related metadata
    flapi = import_flapi(config)
    flapi_host = resolve_flapi_host(config, blpath)

    conn = fl_connect(config, flapi, flapi_host)
    if not conn:
        return None
    scene_path = fl_get_scene_path(config, flapi, conn, blpath)
    if not scene_path:
        return None

    log.verbose( "Opening QueueManager connection" )

    try:
        log.verbose('Trying to open scene %s in read-write mode' % scene_path)
        scene = conn.Scene.open_scene( scene_path, {  flapi.OPENFLAG_DISCARD  })
    except flapi.FLAPIException as ex:
        log.error( "Error opening scene: %s" % ex )
        return None

    scene.start_delta('Add kitsu metadata to shots')

    for baselight_shot in new_shots:
        shot_name = create_kitsu_shot_name(config, baselight_shot)
        shot_data = build_kitsu_shot_data(config, baselight_shot)
        shot_id = baselight_shot.get('shot_id')
        shot = scene.get_shot(shot_id)
        
        qm = conn.QueueManager.create_local()
        ex = conn.Export.create()
        ex.select_shot(shot)
        exSettings = flapi.StillExportSettings()
        exSettings.ColourSpace = "sRGB"
        exSettings.Format = "HD 1920x1080"
        exSettings.Overwrite = flapi.EXPORT_OVERWRITE_REPLACE
        exSettings.Directory = config.get('remote_temp_folder', '/var/tmp')
        exSettings.Frames = flapi.EXPORT_FRAMES_FIRST 
        # exSettings.Filename = "%{Job}/%{Clip}_%{TimelineFrame}"
        exSettings.Filename = str(shot_id)
        exSettings.Source = flapi.EXPORT_SOURCE_SELECTEDSHOTS

        print ('')
        log.verbose( "Submitting to queue" )
        exportInfo = ex.do_export_still( qm, scene, exSettings)
        waitForExportToComplete(qm, exportInfo)
        del ex
        log.verbose( "Closing QueueManager" )
        qm.release()

        file_list = remote_listdir(
            config.get('remote_temp_folder', '/var/tmp'),
            flapi_host.get('flapi_user'),
            flapi_host.get('flapi_hostname')
            )

        thumbnail_file_name = str(shot_id) + '.jpg'
        thumbnail_local_path = ''
        if thumbnail_file_name in file_list:
            # get it over here to upload thumbnail
            thumbnail_remote_path = os.path.join(
                config.get('remote_temp_folder', '/var/tmp'),
                thumbnail_file_name
            )
            thumbnail_local_path = config.get('temp_folder', '/var/tmp')
            if not thumbnail_local_path.endswith(os.path.sep):
                thumbnail_local_path = thumbnail_local_path + os.path.sep
            rsync(
                flapi_host.get('flapi_user'),
                flapi_host.get('flapi_hostname'),
                thumbnail_remote_path,
                thumbnail_local_path
            )
            remote_rm(
                thumbnail_remote_path,
                flapi_host.get('flapi_user'),
                flapi_host.get('flapi_hostname')    
            )
        
        if not thumbnail_local_path:
            log.verbose('No thumbnail generated, skipping shot creation...')
            continue

        new_shot = gazu.shot.new_shot(
            project_dict, 
            baselight_linked_sequence, 
            shot_name,
            data = shot_data
            # data = {'00_shot_id': baselight_shot.get('shot_id')}
        )

        pprint (shot_data)

        task_types = gazu.task.all_task_types()
        shot_task_types = [t for t in task_types if t['for_entity'] == 'Shot']
        shot_task_types = sorted(shot_task_types, key=lambda d: d['priority'])
        task = gazu.task.new_task(new_shot, shot_task_types[0])
        todo = gazu.task.get_task_status_by_short_name("todo")
        comment = gazu.task.add_comment(task, todo, "Add thumbnail")

        preview_file = gazu.task.add_preview(
            task,
            comment,
            os.path.join(
                thumbnail_local_path,
                thumbnail_file_name
            )
        )
        gazu.task.set_main_preview(preview_file)
        # gazu.task.remove_task(task)

        try:
            os.remove(thumbnail_local_path)
        except:
            pass

        new_md_values = {
            kitsu_uid_metadata_obj.Key: new_shot.get('id')
        }

        shot.set_metadata( new_md_values )

        shot.release()

        # shot = scene.get_shot(shot_inf.ShotId)


    scene.end_delta()
    scene.save_scene()
    scene.close_scene()
    scene.release()

    fl_disconnect(config, flapi, flapi_host, conn)
    return


def waitForExportToComplete( qm, exportInfo ):
    for msg in exportInfo.Log:
        if (msg.startswith("Error")):
            print("Export Submission Failed.  %s" % msg);
            return

    print( "Waiting on render job to complete" )
    triesSinceChange = 0
    lastProgress = -1
    maxTries = 20
    while True:
        opstat = qm.get_operation_status( exportInfo.ID )
        triesSinceChange +=1 
        if opstat.Progress != lastProgress:
            triesSinceChange = 0
            lastProgress = opstat.Progress
        dots = ""
        if (triesSinceChange > 0):
            dots = "..."[:(triesSinceChange%3)+1]
        else:
            pass
            # print("")
        print( "\r  Status: {Status} {Progress:.0%} {ProgressText} ".format(**vars(opstat)), end=""), 
        print("%s    " % dots, end=""),
        sys.stdout.flush()
        if opstat.Status == "Done":
            print( "\nExport complete" )
            break
        if triesSinceChange == maxTries:
            print("\nStopped waiting for queue to complete.")
            break
        time.sleep(0.5)

    exportLog = qm.get_operation_log( exportInfo.ID )
    for l in exportLog:
        print( "   %s %s: %s" % (l.Time, l.Message, l.Detail) )

    print( "Archiving operaton" )
    qm.archive_operation ( exportInfo.ID )


def resolve_blpath(config, baselight_linked_sequence):
    log = config.get('log')
    
    data = baselight_linked_sequence.get('data')
    if not isinstance(data, dict):
        log.info('no baselight path found in sequence "%s"' % pformat(baselight_linked_sequence))
        return ''
    blpath = data.get('blpath')
    if not blpath:
        log.info('no baselight path found in sequence "%s"' % pformat(baselight_linked_sequence))
        return ''
    blpath_components = blpath.split(':')
    flapi_hosts = config.get('flapi_hosts')
    if not flapi_hosts:
        log.info('no flapi hosts defined in configuration')
        return ''
    flapi_hosts = {x['flapi_hostname']:x for x in flapi_hosts}
    if blpath_components[0] not in flapi_hosts.keys():
        log.info('host "%s" is not defined in flapi_hosts config file' % blpath_components[0])
        # return

    return blpath



def create_kitsu_shot_name(config, baselight_shot):
    import uuid
    shot_md = baselight_shot.get('shot_md')
    if not shot_md:
        return ((str(uuid.uuid1()).replace('-', '')).upper())[:4]
    rectc_in = shot_md.get('rectc.0')
    if not rectc_in:
        return ((str(uuid.uuid1()).replace('-', '')).upper())[:4]
    return str(rectc_in)

def build_kitsu_shot_data(config, baselight_shot):
    data = {}
    md_descriptors = config.get('metadata_descriptors')
    md_descriptors_by_bl_key = {}
    for md_desc in md_descriptors:
        bl_key = md_desc.get('bl_metadata_key')
        if not bl_key:
            bl_name = md_desc.get('bl_metadata_name')
            if not bl_name:
                continue
            else:
                mddefns = baselight_shot.get('mddefns')
                for md_def in mddefns:
                    name = md_def.Name
                    if name == bl_name:
                        bl_key = md_def.Key
                        md_descriptors_by_bl_key[bl_key] = md_desc
                continue
        md_descriptors_by_bl_key[bl_key] = md_desc
    shot_md = baselight_shot.get('shot_md')
    for bl_key in md_descriptors_by_bl_key.keys():
        kitsu_key = md_descriptors_by_bl_key[bl_key].get('kitsu_key')
        value = str(shot_md.get(bl_key))
        if 'padding' in md_descriptors_by_bl_key[bl_key].keys():
            padding = md_descriptors_by_bl_key[bl_key].get('padding', 0)
            value = value.zfill(padding)
        data[kitsu_key] = value
    return data

def check_or_add_kitsu_metadata_definition(config, blpath):
    log = config.get('log')
    flapi = import_flapi(config)
    flapi_host = resolve_flapi_host(config, blpath)
    conn = fl_connect(config, flapi, flapi_host)
    if not conn:
        return None
        
    scene_path = fl_get_scene_path(config, flapi, conn, blpath)
    if not scene_path:
        return None

    try:
        log.verbose('Opening scene: %s' % scene_path)
        scene = conn.Scene.open_scene( scene_path, { flapi.OPENFLAG_READ_ONLY } )
    except flapi.FLAPIException as ex:
        log.error( "Error opening scene: %s" % ex )
        return None

    md_names = {}
    mddefns = scene.get_metadata_definitions()

    for mdfn in mddefns:
        md_names[mdfn.Name] = mdfn

    if 'kitsu-uid' in md_names.keys():
        log.verbose('kistu-uid metadata columnn already exists in scene: "%s"' % scene.get_scene_pathname())
        scene.close_scene()
        scene.release()    
        fl_disconnect(config, flapi, flapi_host, conn)
        return md_names['kitsu-uid']

    # the scene has no kitsu-id metadata defined
    # try to re-open the scene in rw mode and add this definition
    scene.close_scene()
    scene.release()

    try:
        log.verbose('Trying to open scene %s in read-write mode' % scene_path)
        scene = conn.Scene.open_scene( scene_path )
    except flapi.FLAPIException as ex:
        log.error( "Error opening scene: %s" % ex )
        return None

    log.verbose('Adding kistu-uid metadata columnn to scene: "%s"' % scene.get_scene_pathname())
    scene.start_delta('Add kitsu-id metadata column')
    metadata_obj = scene.add_metadata_defn('kitsu-uid', 'String')
    scene.end_delta()
    scene.save_scene()
    scene.close_scene()
    scene.release()
    fl_disconnect(config, flapi, flapi_host, conn)
    return metadata_obj


def resolve_flapi_host(config, blpath):
    blpath_components = blpath.split(':')
    flapi_hosts = config.get('flapi_hosts')
    flapi_hosts = {x['flapi_hostname']:x for x in flapi_hosts}
    flapi_host = flapi_hosts.get(blpath_components[0])
    if not flapi_host:
        flapi_host = flapi_hosts.get(list(flapi_hosts.keys())[0])
    return flapi_host


def get_baselight_scene_shots(config, blpath):
    log = config.get('log')

    flapi = import_flapi(config)
    flapi_host = resolve_flapi_host(config, blpath)
        
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
            print( "\r Querying metadata for shot %d of %s" % (shot_ix + 1, nshots), end="" )
            # log.verbose("Shot %d:" % shot_ix)
            shot = scene.get_shot(shot_inf.ShotId)
            shot_md = shot.get_metadata(md_keys)
            for key in md_keys:
                if type(shot_md[key]) is list:
                    for list_ix, list_inf in enumerate(shot_md[key]):
                        shot_md[key + '.' + str(list_ix)] = list_inf
                    # print ('%15s: %s: %s:' % (key, type(shot_md[key]), shot_md[key]))
            # shot_md = shot.get_metadata_strings(md_keys)
            mark_ids = shot.get_mark_ids()
            categories = shot.get_categories()

            thumbnail_url = ''
            # thumbnail_url = conn.ThumbnailManager.get_poster_uri(shot, 1, {'DCSpace': 'sRGB'})
            # pprint (thumbnail_url)

            baselight_shots.append(
                {
                    'shot_ix': shot_ix + 1,
                    'shot_id': shot_inf.ShotId,
                    'mddefns': mddefns,
                    'shot_md': shot_md,
                    'mark_ids': mark_ids,
                    'categories': categories,
                    'thumbnail_url': thumbnail_url
                }
            )

            shot.release()
        print ('')

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

    try:
        blpath_components = blpath.split(':')
        bl_hostname = blpath_components[0]
        bl_jobname = blpath_components[1]
        bl_scene_name = blpath_components[-1]
        bl_scene_path = ':'.join(blpath_components[2:])
        bl_scenes_folder = ''.join(blpath_components[2:-1])

        if '*' in bl_scene_name:
            # find the most recent scene
            import re
            log.verbose('finding most recent baselight scene for pattern: %s' % blpath)
            existing_scenes = conn.JobManager.get_scenes(bl_hostname, bl_jobname, bl_scenes_folder)
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
                blpath = bl_hostname + ':' + bl_jobname + ':' + bl_scene_path

        else:
            # we have full scene path and need to check if scene exists

            log.verbose('checking baselight scene: %s' % blpath)

            if not conn.JobManager.scene_exists(bl_hostname, bl_jobname, bl_scene_path):
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
    except:
        log.verbose('unable to get scene path from: %s' % blpath)
        return None


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

def import_flapi(config):
    log = config.get('log')
    flapi_module_path = config.get('flapi_module_path')
    log.verbose('importing flapi from %s' % flapi_module_path)
    try:
        if sys.path[0] != flapi_module_path:
            sys.path.insert(0, flapi_module_path)
        import flapi
        return flapi
    except Exception as e:
        log.error('unable to import filmlight api python module from: %s' % flapi_module_path)
        log.error(e)
