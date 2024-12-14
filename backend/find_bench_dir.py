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
    search_roots = ["/home/frappe", "/workspace"]
    search_depth = 3
    
    for search_root in search_roots:
        try:
            # Check if the search_root exists
            exit_code, _ = container.exec_run(f"test -d {search_root}")
            if exit_code != 0:
                continue

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
            print(f"Error searching for bench directory in {search_root}: {e}")

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

def get_sites(container, bench_dir):
    """Get the list of sites in the Frappe container."""
    exit_code, _ = container.exec_run(f"test -d {bench_dir}/sites")
    if exit_code != 0:
        return []
    cmd = f"sh -c 'ls {bench_dir}/sites | grep -v 'apps' | grep localhost$'"
    exit_code, output = container.exec_run(cmd)
    if exit_code != 0:
        raise Exception(f"Error executing command: {cmd}")
    
    sites = output.decode('utf-8').replace('\r', '').strip().split('\n')
    return [site for site in sites if site]

def get_installed_apps(container, bench_dir, site):
    """Get the list of installed apps for a specific site."""
    cmd = f"bench --site {site} list-apps"
    exit_code, output = container.exec_run(cmd, workdir=bench_dir)
    if exit_code != 0:
        raise Exception(f"Error executing command: {cmd}")
    
    apps = output.decode('utf-8').replace('\r', '').strip().split('\n')
    return [app for app in apps if app]  

def get_available_apps(container, bench_dir):
    """Get the list of available apps in the bench directory."""
    exit_code, _ = container.exec_run(f"test -d {bench_dir}/apps")
    if exit_code != 0:
        return []
    cmd = f"sh -c 'ls {bench_dir}/apps'"
    exit_code, output = container.exec_run(cmd)
    if exit_code != 0:
        raise Exception(f"Error executing command: {cmd}")
    
    apps = output.decode('utf-8').replace('\r', '').strip().split('\n')
    return [app for app in apps if app]  

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
            
            if bench_dir:
                sites = get_sites(container, bench_dir)
                sites_info = []
                for site in sites:
                    installed_apps = get_installed_apps(container, bench_dir, site)
                    sites_info.append({
                        "name": site,
                        "installed_apps": installed_apps
                    })
                
                available_apps = get_available_apps(container, bench_dir)
                
                results.append({
                    "project_name": project_name,
                    "bench_directory": bench_dir,
                    "sites": sites_info,
                    "available_apps": available_apps
                })
            else:
                results.append({
                    "project_name": project_name,
                    "error": "Bench directory not found"
                })
        except Exception as e:
            results.append({
                "container_id": container.id,
                "error": str(e)
            })

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()

