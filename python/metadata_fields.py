import os
import sys
import time
from pprint import pprint, pformat

def set_metadata_fields(config):
    log = config.get('log')
    import gazu

    config_gazu = config.get('gazu')
    if not config_gazu:
        return
    host = config_gazu.get('host')
    name = config_gazu.get('name')
    password = config_gazu.get('password')

    metadata_descriptors = config.get('metadata_descriptors')

    while True:
        try:
            gazu.set_host(host)
            gazu.log_in(name, password)

            projects = gazu.project.all_open_projects()
            for project in projects:
                descriptors_api_path = '/data/projects/' + project.get('id') + '/metadata-descriptors'
                project_descriptor_data = gazu.client.get(descriptors_api_path)
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

                        gazu.client.post(descriptors_api_path, data)

            time.sleep(4)
            gazu.log_out()
        except KeyboardInterrupt:
            return
        except Exception as e:
            log.error('exception in "set_metadata_fields": %s' % pformat(e))
            time.sleep(4)