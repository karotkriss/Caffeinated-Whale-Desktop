# ToDo: get site db user and password 

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
    search_roots = ["/home/frappe", "/workspace", "/frappe", "/app"]
    search_depth = 3
    
    for search_root in set(search_roots):  # Use set to remove duplicates
        try:
            # Check if directory exists
            exit_code, _ = container.exec_run(f"test -d {search_root}")
            if exit_code != 0:
                print(f"Directory {search_root} does not exist")
                continue

            # List directories to get more context
            list_cmd = f"find {search_root} -maxdepth {search_depth} -type d -not -path '*/\.*'"
            exit_code, output = container.exec_run(list_cmd)

            if exit_code != 0:
                print(f"Error executing find command in {search_root}")
                continue

            # Decode and process output
            directories = output.decode("utf-8").splitlines()
            print(f"Searching in {search_root}, found {len(directories)} directories")

            for dirpath in directories:
                # Extended logging for diagnostics
                print(f"Checking directory: {dirpath}")
                
                # Check for bench-specific files/directories
                checks = [
                    f"test -d {dirpath}/sites",
                    f"test -d {dirpath}/apps",
                    f"test -f {dirpath}/sites/common_site_config.json"
                ]
                
                is_bench = all(
                    container.exec_run(check)[0] == 0 
                    for check in checks
                )
                
                if is_bench:
                    print(f"Found bench directory: {dirpath}")
                    return dirpath

        except Exception as e:
            print(f"Error searching for bench directory in {search_root}: {e}")

        # If no bench directory found
        print("No bench directory found. Possible reasons:")
        print("1. Bench may be installed in a non-standard location")
        print("2. Container might not have Frappe/Bench installed")
        print("3. Search roots and depth may need adjustment")
        print("4. Container might not be running")
    
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

def update_database(project_name=None, specific_site=None, update_bench=True, update_sites=True, update_apps=True):
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
            # Get all sites if no specific site is provided
            sites = get_sites(container, bench_dir) if update_sites else existing_info.get("sites", []) if existing_info else []
            
            # Filter sites if a specific site is provided
            if specific_site:
                sites = [site for site in sites if site == specific_site]
                if not sites:
                    print(f"Site {specific_site} not found in project {current_project}")
                    continue

            apps = get_available_apps(container, bench_dir) if update_apps else existing_info.get("available_apps", []) if existing_info else []
            
            update_project(current_project, container.id, bench_dir, sites, apps)
            print(f"Updated information for project: {current_project}")
            
            # If a specific site was updated, print its details
            if specific_site:
                print(f"Updated site: {specific_site}")
        else:
            print(f"No bench directory found for project: {current_project}")

def main():
    parser = argparse.ArgumentParser(description="Update Frappe instance information in the database")
    parser.add_argument("-p", "--project", help="Docker Compose project name to update (default: update all projects)")
    parser.add_argument("-s", "--site", help="Specific site to update within a project")
    parser.add_argument("--bench", action="store_true", help="Update bench directory information")
    parser.add_argument("--sites", action="store_true", help="Update sites information")
    parser.add_argument("--apps", action="store_true", help="Update available apps information")
    parser.add_argument("--all", action="store_true", help="Update all information (default if no specific update is selected)")

    args = parser.parse_args()

    # Validate site update requires project specification
    if args.site and not args.project:
        parser.error("--site requires --project to be specified")

    update_bench = args.bench or args.all
    update_sites = args.sites or args.all
    update_apps = args.apps or args.all

    # If no specific update is selected, update all
    if not (update_bench or update_sites or update_apps):
        update_bench = update_sites = update_apps = True

    update_database(
        project_name=args.project, 
        specific_site=args.site, 
        update_bench=update_bench, 
        update_sites=update_sites, 
        update_apps=update_apps
    )

if __name__ == "__main__":
    main()