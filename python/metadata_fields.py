import os
import sys
import time
from pprint import pprint, pformat

def set_metadata_fields(config):
    import gazu

    config_gazu = config.get('gazu')
    if not config_gazu:
        return
    host = config_gazu.get('host')
    name = config_gazu.get('name')
    password = config_gazu.get('password')

    gazu.set_host(host)
    gazu.log_in(name, password)

    metadata_descriptors = config.get('metadata_descriptors')
    pprint (metadata_descriptors)
    sys.exit()

    while True:
        try:
            # print ('[' + datetime.now().strftime("%Y%m%d %H:%M") + ']\n' + 'Hello from Kitsu-Robot' + '\n')
            projects = gazu.project.all_open_projects()
            for project in projects:
                descriptors_api_path = '/data/projects/' + project.get('id') + '/metadata-descriptors'
                project_descriptor_data = gazu.client.get(descriptors_api_path)
                project_descriptor_names = [x['name'] for x in project_descriptor_data]
                
                if 'test' not in project_descriptor_names:
                    data = {
                        'name': 'test',
                        'choices': [],
                        'for_client': False,
                        'entity_type': 'Shot',
                        'departments': []
                    }
                    gazu.client.post(descriptors_api_path, data)
            # data = gazu.client.fetch_all("shots")
            # pprint (data)
            # pprint (dir(gazu))
            time.sleep(4)
        except KeyboardInterrupt:
            return