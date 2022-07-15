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
        if not os.path.isdir(flapi_module_path):
            app_path = os.path.dirname(os.path.abspath(__file__))
            flapi_module_path = os.path.join(
                os.path.dirname(app_path),
                'flapi',
                'python'
            )
    else:
        flapi_module_path = os.path.join(
            bl_path,
            'share/flapi/python/'
        )

    if not os.path.isdir(flapi_module_path):
        print ('unable to find flapi python module')
        sys.exit()

    data['flapi_host'] = 'localhost'
    
    data['flapi_module_path'] = flapi_module_path

def get_config_data(args):
    config_file_path = args.get('config file')
    if not (config_file_path):
        file_path = os.path.abspath(__file__)
        config_dir = os.path.dirname(os.path.dirname(file_path))
        config_file_path = os.path.join(config_dir, 'config.json')

    config = None
    
    if os.path.isfile(config_file_path):
        try:
            with open(config_file_path, 'r') as config_file:
                config = json.load(config_file)
                config_file.close()
        except Exception as e:
            print('[WARNING] Unable to read config file %s' % config_file_path)
            print(e)

    data = default_config_data()
    for key in args.keys():
        data[key] = args.get(key)

    if not isinstance (config, dict):
        pass
    else:
        for key in config.keys():
            data[key] = config.get(key)
    return data