# create_instance.py
import json
import sys
import docker

def create_frappe_instance(config):
    """Create a new Frappe Docker container."""
    client = docker.from_env()
    
    try:
        container = client.containers.run(
            "frappe/frappe-docker:latest",
            name=config['projectName'],
            ports={
                '80/tcp': config['port']
            },
            detach=True,
            environment={
                'SITE_NAME': config['siteName']
            }
        )
        print(json.dumps({
            'status': 'success',
            'containerId': container.id,
            'projectName': config['projectName']
        }))
    except Exception as e:
        print(json.dumps({
            'status': 'error',
            'message': str(e)
        }))