import os
import sys
import json
import time
from copy import deepcopy

from .common import log
from pprint import pprint, pformat

def default_config_data():
    data = {}

    # Baselight Specific path definitions
    '''
    if sys.platform == 'darwin':
        bl_path = '/Applications/Baselight/5.3.14832'
        data['bl_path'] = bl_path
        data['bl_flls_path'] = os.path.join(bl_path, 'Utilities/Tools/fl-ls')
        data['bl_import_path'] = os.path.join(bl_path, 'Utilities/Tools/bl-import')
        data['bl_render_path'] = os.path.join(bl_path, 'Utilities/Tools/bl-render')
    else:
    '''
    
    bl_path = '/usr/fl/baselight'
    data['bl_path'] = bl_path
    data['bl_flls_path'] = os.path.join(bl_path, 'bin/fl-ls')
    data['bl_import_path'] = os.path.join(bl_path, 'bin/bl-import')
    data['bl_render_path'] = os.path.join(bl_path, 'bin/bl-render')

    if sys.platform == 'darwin':
        flapi_module_path = os.path.join(
            bl_path,
            'Baselight-' + os.path.basename(bl_path) + '.app',
            'Contents/share/flapi/python/'
        )
    else:
        flapi_module_path = os.path.join(
            bl_path,
            'share/flapi/python/'
        )

    if not os.path.isdir(flapi_module_path):
        app_path = os.path.dirname(os.path.abspath(__file__))
        flapi_module_path = os.path.join(
            os.path.dirname(app_path),
            'flapi',
            'python'
        )

    if not os.path.isdir(flapi_module_path):
        print ('unable to find flapi python module')
        sys.exit()
    
    data['flapi_module_path'] = flapi_module_path

    return data

def get_config_data(config_folder_path):
    # print ('reading config files from ' + config_folder_path)
    data = default_config_data()
    data['config_folder_path'] = config_folder_path
    
    if not os.path.isdir(config_folder_path):
        return data
    
    config_files = os.listdir(config_folder_path)
    if not config_files:
        return data
    
    for config_file_name in config_files:
        config_file_path = os.path.join(
            config_folder_path,
            config_file_name
        )

        try:
            with open(config_file_path, 'r') as config_file:
                config = json.load(config_file)
                config_file.close()
        except Exception as e:
            print('[WARNING] Unable to read config file %s' % config_file_path)
            print(e)

        name, ext = os.path.splitext(config_file_name)
        data[name] = deepcopy(config)

    return data

def config_reader(app_data):
    while True:
        try:
            app_config = app_data['config']
            app_location = app_config['app_location']
            config_folder_path = os.path.join(app_location, 'config')
            current_config = get_config_data(config_folder_path)
            for config_key in current_config.keys():
                app_config[config_key] = current_config[config_key]
            app_data['config'] = app_config
            time.sleep(4)
        except KeyboardInterrupt:
            return
        except Exception as e:
            log('exception in "sequence_sync": %s' % pformat(e))
            time.sleep(4)