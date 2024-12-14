import docker
import json
import argparse
import sys

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
                continue  # Skip this search_root if it doesn't exist

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

def get_frappe_containers(project_name=None):
    """Retrieve all containers labeled as Frappe service containers."""
    try:
        client = docker.from_env()
        filters = {"label": "com.docker.compose.service=frappe"}
        if project_name:
            filters["label"] = f"com.docker.compose.project={project_name}"
        containers = client.containers.list(filters=filters)
        return containers
    except docker.errors.DockerException as e:
        print(f"Error interacting with Docker: {e}")
        return []

def get_sites(container, bench_dir):
    """Get the list of sites in the Frappe container."""
    exit_code, _ = container.exec_run(f"test -d {bench_dir}/sites")
    if exit_code != 0:
        return []
    cmd = f"bash -c 'ls {bench_dir}/sites | grep -v 'apps' | grep -v '.json' | grep -v 'assets''"
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
    return [app for app in apps if app]  # Remove any empty strings

def get_available_apps(container, bench_dir):
    """Get the list of available apps in the bench directory."""
    exit_code, _ = container.exec_run(f"test -d {bench_dir}/apps")
    if exit_code != 0:
        return []
    cmd = f"bash -c 'ls {bench_dir}/apps'"
    exit_code, output = container.exec_run(cmd)
    if exit_code != 0:
        raise Exception(f"Error executing command: {cmd}")
    
    apps = output.decode('utf-8').replace('\r', '').strip().split('\n')
    return [app for app in apps if app]

def get_project_sites(project_name):
    """Get all sites for a specific project."""
    containers = get_frappe_containers(project_name)
    if not containers:
        return {"error": f"No Frappe containers found for project {project_name}"}

    sites = []
    for container in containers:
        bench_dir = find_bench_directory_in_container(container)
        if bench_dir:
            sites.extend(get_sites(container, bench_dir))
    
    return {"sites": sites}

def get_site_apps(project_name, site_name):
    """Get installed apps for a specific site in a project."""
    containers = get_frappe_containers(project_name)
    if not containers:
        return {"error": f"No Frappe containers found for project {project_name}"}

    for container in containers:
        bench_dir = find_bench_directory_in_container(container)
        if bench_dir:
            sites = get_sites(container, bench_dir)
            if site_name in sites:
                apps = get_installed_apps(container, bench_dir, site_name)
                return {"site": site_name, "installed_apps": apps}
    
    return {"error": f"Site {site_name} not found in project {project_name}"}

def get_project_apps(project_name):
    """Get all available apps for a specific project."""
    containers = get_frappe_containers(project_name)
    if not containers:
        return {"error": f"No Frappe containers found for project {project_name}"}

    all_apps = set()
    for container in containers:
        bench_dir = find_bench_directory_in_container(container)
        if bench_dir:
            apps = get_available_apps(container, bench_dir)
            all_apps.update(apps)
    
    return {"available_apps": list(all_apps)}

def get_all_projects_info():
    """Get information for all Frappe projects."""
    containers = get_frappe_containers()
    if not containers:
        return {"error": "No Frappe containers found"}

    projects = {}
    for container in containers:
        project_name = container.labels.get("com.docker.compose.project", "unknown")
        if project_name not in projects:
            projects[project_name] = {"sites": [], "available_apps": set()}

        bench_dir = find_bench_directory_in_container(container)
        if bench_dir:
            sites = get_sites(container, bench_dir)
            projects[project_name]["sites"].extend(sites)
            apps = get_available_apps(container, bench_dir)
            projects[project_name]["available_apps"].update(apps)

    # Convert sets to lists for JSON serialization
    for project in projects.values():
        project["available_apps"] = list(project["available_apps"])

    return {"projects": projects}

def get_site_info(project_name, site_name):
    """Get detailed information for a specific site."""
    containers = get_frappe_containers(project_name)
    if not containers:
        return {"error": f"No Frappe containers found for project {project_name}"}

    for container in containers:
        bench_dir = find_bench_directory_in_container(container)
        if bench_dir:
            sites = get_sites(container, bench_dir)
            if site_name in sites:
                installed_apps = get_installed_apps(container, bench_dir, site_name)
                # You can add more site-specific information here
                return {
                    "site": site_name,
                    "project": project_name,
                    "bench_directory": bench_dir,
                    "installed_apps": installed_apps
                }
    
    return {"error": f"Site {site_name} not found in project {project_name}"}

def main():
    parser = argparse.ArgumentParser(description="Frappe Instance Info")
    parser.add_argument("-p", "--project", help="Docker Compose project name")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--get-sites", action="store_true", help="Get all sites for the project")
    group.add_argument("--get-site-app", metavar="SITE", help="Get installed apps for a specific site")
    group.add_argument("--get-apps", action="store_true", help="Get all available apps for the project")
    group.add_argument("--get-site-info", metavar="SITE", help="Get detailed information for a specific site")

    args = parser.parse_args()

    try:
        if args.project:
            if args.get_sites:
                result = get_project_sites(args.project)
            elif args.get_site_app:
                result = get_site_apps(args.project, args.get_site_app)
            elif args.get_apps:
                result = get_project_apps(args.project)
            elif args.get_site_info:
                result = get_site_info(args.project, args.get_site_info)
            else:
                # If no specific action is provided, return all info for the project
                result = get_project_apps(args.project)
                result.update(get_project_sites(args.project))
        else:
            # If no project is specified, return info for all projects
            result = get_all_projects_info()

        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

