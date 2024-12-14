import sqlite3
import json
from pathlib import Path

DB_FILE = Path(__file__).parent / "frappe_instances.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS containers (
        id INTEGER PRIMARY KEY,
        project_id INTEGER,
        container_id TEXT UNIQUE NOT NULL,
        bench_dir TEXT,
        FOREIGN KEY (project_id) REFERENCES projects (id)
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sites (
        id INTEGER PRIMARY KEY,
        container_id INTEGER,
        name TEXT NOT NULL,
        UNIQUE(container_id, name),
        FOREIGN KEY (container_id) REFERENCES containers (id)
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS apps (
        id INTEGER PRIMARY KEY,
        container_id INTEGER,
        name TEXT NOT NULL,
        UNIQUE(container_id, name),
        FOREIGN KEY (container_id) REFERENCES containers (id)
    )
    ''')
    conn.commit()
    conn.close()

def update_project(project_name, container_id, bench_dir, sites, apps):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Insert or update project
    cursor.execute('INSERT OR IGNORE INTO projects (name) VALUES (?)', (project_name,))
    cursor.execute('SELECT id FROM projects WHERE name = ?', (project_name,))
    project_id = cursor.fetchone()[0]
    
    # Insert or update container
    cursor.execute('''
    INSERT OR REPLACE INTO containers (project_id, container_id, bench_dir)
    VALUES (?, ?, ?)
    ''', (project_id, container_id, bench_dir))
    container_db_id = cursor.lastrowid
    
    # Update sites
    cursor.execute('DELETE FROM sites WHERE container_id = ?', (container_db_id,))
    for site in set(sites):  # Use set to remove duplicates
        cursor.execute('INSERT OR IGNORE INTO sites (container_id, name) VALUES (?, ?)', (container_db_id, site))
    
    # Update apps
    cursor.execute('DELETE FROM apps WHERE container_id = ?', (container_db_id,))
    for app in set(apps):  # Use set to remove duplicates
        cursor.execute('INSERT OR IGNORE INTO apps (container_id, name) VALUES (?, ?)', (container_db_id, app))
    
    conn.commit()
    conn.close()

def get_project_info(project_name):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT c.bench_dir, s.name as site_name, GROUP_CONCAT(DISTINCT a.name) as apps
    FROM projects p
    JOIN containers c ON p.id = c.project_id
    LEFT JOIN sites s ON c.id = s.container_id
    LEFT JOIN apps a ON c.id = a.container_id
    WHERE p.name = ?
    GROUP BY c.id, s.id
    ''', (project_name,))
    
    rows = cursor.fetchall()
    if not rows:
        return None
    
    result = {
        "project_name": project_name,
        "bench_directory": rows[0]['bench_dir'],
        "sites": [],
        "available_apps": set()
    }
    
    for row in rows:
        if row['site_name']:
            result["sites"].append(row['site_name'])
        if row['apps']:
            result["available_apps"].update(row['apps'].split(','))
    
    result["available_apps"] = list(result["available_apps"])
    
    conn.close()
    return result

def get_all_projects_info():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT p.name as project_name, c.bench_dir, s.name as site_name, GROUP_CONCAT(DISTINCT a.name) as apps
    FROM projects p
    JOIN containers c ON p.id = c.project_id
    LEFT JOIN sites s ON c.id = s.container_id
    LEFT JOIN apps a ON c.id = a.container_id
    GROUP BY p.id, c.id, s.id
    ''')
    
    rows = cursor.fetchall()
    projects = {}
    
    for row in rows:
        project_name = row['project_name']
        if project_name not in projects:
            projects[project_name] = {
                "bench_directory": row['bench_dir'],
                "sites": [],
                "available_apps": set()
            }
        
        if row['site_name']:
            projects[project_name]["sites"].append(row['site_name'])
        if row['apps']:
            projects[project_name]["available_apps"].update(row['apps'].split(','))
    
    for project in projects.values():
        project["available_apps"] = list(project["available_apps"])
    
    conn.close()
    return {"projects": projects}

# Initialize the database when this module is imported
init_db()

