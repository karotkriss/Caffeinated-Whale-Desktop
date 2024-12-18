import docker
import json
import argparse
from datetime import datetime
import secrets
import string
from db_operations import (
    get_db_connection,
    create_or_update_project,
    create_or_update_container,
    create_or_update_instance,
    create_or_update_site,
    create_or_update_app,
    create_or_update_instance_app,
    create_site_app,
    get_site_id
)

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
            exit_code, _ = container.exec_run(f"test -d {search_root}")
            if exit_code != 0:
                print(f"Directory {search_root} does not exist")
                continue

            list_cmd = f"find {search_root} -maxdepth {search_depth} -type d -not -path '*/\.*'"
            exit_code, output = container.exec_run(list_cmd)

            if exit_code != 0:
                print(f"Error executing find command in {search_root}")
                continue

            directories = output.decode("utf-8").splitlines()
            print(f"Searching in {search_root}, found {len(directories)} directories")

            for dirpath in directories:
                print(f"Checking directory: {dirpath}")
                
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

    print("No bench directory found. Possible reasons:")
    print("1. Bench may be installed in a non-standard location")
    print("2. Container might not have Frappe/Bench installed")
    print("3. Search roots and depth may need adjustment")
    print("4. Container might not be running")
    
    return None

def get_sites(container, bench_dir):
    sites = []
    cmd = f"find {bench_dir}/sites -maxdepth 1 -mindepth 1 -type d"
    exit_code, output = container.exec_run(cmd)
    if exit_code != 0:
        raise Exception(f"Error executing command: {cmd}")
    
    potential_sites = output.decode('utf-8').strip().split('\n')
    
    for site_path in potential_sites:
        site_name = site_path.split('/')[-1]
        if site_name in ['assets', 'apps']:
            continue
        
        # Check for required folders and files
        required_items = ['locks', 'logs', 'private', 'public', 'site_config.json']
        is_valid_site = all(
            container.exec_run(f"test -e {site_path}/{item}")[0] == 0
            for item in required_items
        )
        
        if is_valid_site:
            # Read site_config.json
            cat_cmd = f"cat {site_path}/site_config.json"
            exit_code, config_output = container.exec_run(cat_cmd)
            if exit_code == 0:
                try:
                    site_config = json.loads(config_output.decode('utf-8'))
                    sites.append({
                        'name': site_name,
                        'db_name': site_config.get('db_name', ''),
                        'db_password': site_config.get('db_password', ''),
                        'db_type': site_config.get('db_type', ''),
                        'developer_mode': site_config.get('developer_mode', 0)
                    })
                except json.JSONDecodeError:
                    print(f"Error parsing site_config.json for {site_name}")
            else:
                print(f"Error reading site_config.json for {site_name}")
    
    return sites

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

def generate_db_password():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(16))

def update_database(project_name=None, specific_site=None, update_bench=True, update_sites=True, update_apps=True):
    client = docker.from_env()
    filters = {"label": "com.docker.compose.service=frappe"}
    if project_name:
        filters["label"] = f"com.docker.compose.project={project_name}"
    containers = client.containers.list(filters=filters)

    for container in containers:
        current_project = container.labels.get("com.docker.compose.project", "unknown")
        project_id = create_or_update_project(current_project, "Frappe project")

        container_id = create_or_update_container(project_id, container.id, "frappe", container.status)
        
        bench_dir = find_bench_directory_in_container(container) if update_bench else None
        
        if bench_dir:
            instance_id = create_or_update_instance(container_id, current_project, bench_dir, "active", "latest")
            
            if update_sites:
                sites = get_sites(container, bench_dir)
                for site in sites:
                    if not specific_site or site['name'] == specific_site:
                        create_or_update_site(
                            instance_id,
                            container_id,
                            site['name'],
                            f"{site['name']}.localhost",
                            site['db_name'],
                            site['db_password'],
                            "active",
                            "production",
                            site['developer_mode'],
                            site['db_type']
                        )
            
            if update_apps:
                apps = get_available_apps(container, bench_dir)
                for app in apps:
                    app_id = create_or_update_app(app, "", "latest", "custom", datetime.now())
                    create_or_update_instance_app(instance_id, app_id, "latest", "installed", "manual")
                    
                    if update_sites:
                        for site in sites:
                            if not specific_site or site['name'] == specific_site:
                                site_id = get_site_id(instance_id, site['name'])
                                if site_id:
                                    create_site_app(site_id, app_id, "latest", "installed", "")

            print(f"Updated information for project: {current_project}")
            
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

    if args.site and not args.project:
        parser.error("--site requires --project to be specified")

    update_bench = args.bench or args.all
    update_sites = args.sites or args.all
    update_apps = args.apps or args.all

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

