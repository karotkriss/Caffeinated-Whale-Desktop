import sys
import json
import docker
import os

def delete_frappe_instance(project_name):
    client = docker.from_env()

    try:
        # Stop and remove containers
        containers = client.containers.list(all=True, filters={'label': f'com.docker.compose.project={project_name}'})
        for container in containers:
            container.stop()
            container.remove()

        # Remove volumes
        volumes = client.volumes.list(filters={'label': f'com.docker.compose.project={project_name}'})
        for volume in volumes:
            volume.remove()

        # Remove networks
        networks = client.networks.list(filters={'label': f'com.docker.compose.project={project_name}'})
        for network in networks:
            network.remove()

        # Remove project directory
        project_dir = os.path.join(os.path.expanduser('~'), 'frappe-projects', project_name)
        if os.path.exists(project_dir):
            os.system(f'rm -rf {project_dir}')

        return json.dumps({"status": "success", "message": f"Instance {project_name} deleted successfully"})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Project name not provided"}))
    else:
        project_name = sys.argv[1]
        print(delete_frappe_instance(project_name))

