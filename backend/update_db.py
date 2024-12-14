import docker
import json
import argparse
from db_operations import update_project, get_project_info

def is_bench_directory(container, path):
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
    search_roots = ["/home/frappe", "/workspace"]
    search_depth = 3
    
    for search_root in search_roots:
        try:
            exit_code, _ = container.exec_run(f"test -d {search_root}")
            if exit_code != 0:
                continue

            cmd = f"find {search_root} -maxdepth {search_depth} -type d"
            exit_code, output = container.exec_run(cmd)

            if exit_code != 0:
                raise Exception(f"Error executing command: {cmd}")

            for dirpath in output.decode("utf-8").splitlines():
                if is_bench_directory(container, dirpath):
                    return dirpath

        except Exception as e:
            print(f"Error searching for bench directory in {search_root}: {e}")

    return None

def get_sites(container, bench_dir):
    exit_code, _ = container.exec_run(f"test -d {bench_dir}/sites")
    if exit_code != 0:
        return []
    cmd = f"bash -c 'ls {bench_dir}/sites | grep -v 'apps' | grep -v '.json' | grep -v 'assets''"
    exit_code, output = container.exec_run(cmd)
    if exit_code != 0:
        raise Exception(f"Error executing command: {cmd}")
    
    sites = output.decode('utf-8').replace('\r', '').strip().split('\n')
    return [site for site in sites if site]

def get_available_apps(container, bench_dir):
    exit_code, _ = container.exec_run(f"test -d {bench_dir}/apps")
    if exit_code != 0:
        return []
    cmd = f"bash -c 'ls {bench_dir}/apps'"
    exit_code, output = container.exec_run(cmd)
    if exit_code != 0:
        raise Exception(f"Error executing command: {cmd}")
    
    apps = output.decode('utf-8').replace('\r', '').strip().split('\n')
    return [app for app in apps if app]

def update_database(project_name=None, update_bench=True, update_sites=True, update_apps=True):
    client = docker.from_env()
    filters = {"label": "com.docker.compose.service=frappe"}
    if project_name:
        filters["label"] = f"com.docker.compose.project={project_name}"
    containers = client.containers.list(filters=filters)

    for container in containers:
        current_project = container.labels.get("com.docker.compose.project", "unknown")
        existing_info = get_project_info(current_project)

        bench_dir = find_bench_directory_in_container(container) if update_bench else existing_info.get("bench_directory") if existing_info else None
        
        if bench_dir:
            sites = get_sites(container, bench_dir) if update_sites else existing_info.get("sites", []) if existing_info else []
            apps = get_available_apps(container, bench_dir) if update_apps else existing_info.get("available_apps", []) if existing_info else []
            update_project(current_project, container.id, bench_dir, sites, apps)
            print(f"Updated information for project: {current_project}")
        else:
            print(f"No bench directory found for project: {current_project}")

def main():
    parser = argparse.ArgumentParser(description="Update Frappe instance information in the database")
    parser.add_argument("-p", "--project", help="Docker Compose project name to update (default: update all projects)")
    parser.add_argument("--bench", action="store_true", help="Update bench directory information")
    parser.add_argument("--sites", action="store_true", help="Update sites information")
    parser.add_argument("--apps", action="store_true", help="Update available apps information")
    parser.add_argument("--all", action="store_true", help="Update all information (default if no specific update is selected)")

    args = parser.parse_args()

    update_bench = args.bench or args.all
    update_sites = args.sites or args.all
    update_apps = args.apps or args.all

    # If no specific update is selected, update all
    if not (update_bench or update_sites or update_apps):
        update_bench = update_sites = update_apps = True

    update_database(args.project, update_bench, update_sites, update_apps)

if __name__ == "__main__":
    main()

