import docker
import json
import argparse
import sys
from db_operations import get_project_info, get_all_projects_info

def get_site_apps(project_name, site_name):
    project_info = get_project_info(project_name)
    if not project_info:
        return {"error": f"No information found for project {project_name}"}
    
    if site_name not in project_info["sites"]:
        return {"error": f"Site {site_name} not found in project {project_name}"}
    
    # In this simplified version, we're assuming all apps are installed on all sites
    # For a more accurate representation, you might need to modify the database schema
    return {"site": site_name, "installed_apps": project_info["available_apps"]}

def get_site_info(project_name, site_name):
    project_info = get_project_info(project_name)
    if not project_info:
        return {"error": f"No information found for project {project_name}"}
    
    if site_name not in project_info["sites"]:
        return {"error": f"Site {site_name} not found in project {project_name}"}
    
    return {
        "site": site_name,
        "project": project_name,
        "bench_directory": project_info["bench_directory"],
        "installed_apps": project_info["available_apps"]  # Simplified, as mentioned above
    }

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
            project_info = get_project_info(args.project)
            if not project_info:
                raise Exception(f"No information found for project {args.project}")
            
            if args.get_sites:
                result = {"sites": project_info["sites"]}
            elif args.get_site_app:
                result = get_site_apps(args.project, args.get_site_app)
            elif args.get_apps:
                result = {"available_apps": project_info["available_apps"]}
            elif args.get_site_info:
                result = get_site_info(args.project, args.get_site_info)
            else:
                result = project_info
        else:
            result = get_all_projects_info()

        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

