import docker
import json


def is_bench_directory(container, path):
    """Validate if a directory is a bench directory inside the container."""
    required_files = [
        "sites",
        "apps",
        "sites/common_site_config.json",
    ]
    try:
        for file in required_files:
            exit_code, _ = container.exec_run(f"test -e {path}/{file}")
            if exit_code != 0:
                return False
        return True
    except Exception as e:
        print(f"Error validating bench directory: {e}")
        return False


def find_bench_directory_in_container(container):
    """Search for the bench directory inside the container."""
    search_root = "/home/frappe"
    search_depth = 3
    try:
        # Run the find command in the container
        cmd = f"find {search_root} -maxdepth {search_depth} -type d"
        exit_code, output = container.exec_run(cmd)

        if exit_code != 0:
            raise Exception(f"Error executing command: {cmd}")

        # Process the output and validate directories
        for dirpath in output.decode("utf-8").splitlines():
            if is_bench_directory(container, dirpath):
                return dirpath

    except Exception as e:
        print(f"Error searching for bench directory: {e}")
        return None

    return None


def get_frappe_containers():
    """Retrieve all containers labeled as Frappe service containers."""
    try:
        client = docker.from_env()
        containers = client.containers.list(
            filters={"label": "com.docker.compose.service=frappe"}
        )
        return containers
    except docker.errors.DockerException as e:
        print(f"Error interacting with Docker: {e}")
        return []


def main():
    frappe_containers = get_frappe_containers()
    if not frappe_containers:
        print(json.dumps({"error": "No Frappe containers found"}))
        return

    results = []
    for container in frappe_containers:
        try:
            project_name = container.labels.get("com.docker.compose.project", "unknown")
            bench_dir = find_bench_directory_in_container(container)
            results.append({"project_name": project_name, "bench_directory": bench_dir})
        except Exception as e:
            results.append({"container_id": container.id, "error": str(e)})

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
