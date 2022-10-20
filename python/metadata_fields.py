import os
import sys
import time
from .config import get_config_data
from pprint import pprint, pformat

def set_metadata_fields(config):
    log = config.get('log')
    import gazu

    while True:
        # read config again in case of changes
        config.update(get_config_data(config.get('config_folder_path')))
        
        config_gazu = config.get('gazu')
        if not config_gazu:
            return
        host = config_gazu.get('host')
        name = config_gazu.get('name')
        password = config_gazu.get('password')
        metadata_descriptors = config.get('metadata_descriptors')

        try:
            gazu_client = gazu.client.create_client(host)
            gazu.log_in(name, password, client = gazu_client)

            projects = gazu.project.all_open_projects(client = gazu_client)
            for project in projects:
                descriptors_api_path = '/data/projects/' + project.get('id') + '/metadata-descriptors'
                project_descriptor_data = gazu.client.get(descriptors_api_path, client = gazu_client)
                project_descriptor_names = [x['name'] for x in project_descriptor_data]
                
                for metadata_descriptor in metadata_descriptors:
                    if metadata_descriptor.get('name') not in project_descriptor_names:
                        data = {
                            'choices': [],
                            'for_client': False,
                            'entity_type': 'Shot',
                            'departments': []
                        }

                        for key in metadata_descriptor.keys():
                            data[key] = metadata_descriptor[key]

                        gazu.client.post(descriptors_api_path, data, client = gazu_client)

            time.sleep(4)
            gazu.log_out(client=gazu_client)
        except KeyboardInterrupt:
            return
        except Exception as e:
            log.error('exception in "set_metadata_fields": %s' % pformat(e))
            time.sleep(4)