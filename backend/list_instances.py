import docker
import json

def list_docker_compose_projects(service_name="frappe"):
    client = docker.from_env()
    projects = {}

    try:
        containers = client.containers.list(all=True)

        for container in containers:
            labels = container.labels
            project_name = labels.get('com.docker.compose.project', None)
            service = labels.get('com.docker.compose.service', None)

            if service == service_name and project_name:
                if project_name not in projects:
                    projects[project_name] = {"ports": [], "status": container.status}

                ports = container.attrs['NetworkSettings']['Ports']
                if not ports:
                    ports = container.attrs['HostConfig']['PortBindings']

                for container_port, bindings in ports.items():
                    if bindings:
                        for binding in bindings:
                            host_port = binding['HostPort']
                            if host_port not in projects[project_name]["ports"]:
                                projects[project_name]["ports"].append(host_port)

    except docker.errors.DockerException as e:
        print(f"Error interacting with Docker: {e}")

    return [{"projectName": name, "ports": data["ports"], "status": data["status"]} for name, data in projects.items()]

if __name__ == "__main__":
    service_name = "frappe"
    projects = list_docker_compose_projects(service_name=service_name)
    print(json.dumps(projects))

