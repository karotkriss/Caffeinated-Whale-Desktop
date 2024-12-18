import sqlite3
import logging
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database file path
DB_FILE = Path(__file__).parent / "frappe_instances.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create PROJECTS table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PROJECTS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create CONTAINERS table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CONTAINERS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        container_id TEXT UNIQUE NOT NULL,
        container_type TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES PROJECTS (id)
    )
    ''')

    # Create INSTANCES table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS INSTANCES (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        container_id INTEGER,
        name TEXT UNIQUE NOT NULL,
        directory TEXT,
        db_root_password TEXT,
        status TEXT,
        version TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (container_id) REFERENCES CONTAINERS (id)
    )
    ''')

    # Create SITES table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SITES (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        instance_id INTEGER,
        container_id INTEGER,
        name TEXT UNIQUE NOT NULL,
        domain TEXT UNIQUE NOT NULL,
        status TEXT,
        environment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (instance_id) REFERENCES INSTANCES (id),
        FOREIGN KEY (container_id) REFERENCES CONTAINERS (id)
    )
    ''')

    # Create APPS table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS APPS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_name TEXT UNIQUE NOT NULL,
        remote_url TEXT,
        version TEXT,
        category TEXT,
        released_at TIMESTAMP
    )
    ''')

    # Create INSTANCE_APPS table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS INSTANCE_APPS (
        instance_id INTEGER,
        app_id INTEGER,
        version TEXT,
        status TEXT,
        installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        install_method TEXT,
        PRIMARY KEY (instance_id, app_id),
        FOREIGN KEY (instance_id) REFERENCES INSTANCES (id),
        FOREIGN KEY (app_id) REFERENCES APPS (id)
    )
    ''')

    # Create SITE_APPS table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SITE_APPS (
        site_id INTEGER,
        app_id INTEGER,
        version TEXT,
        status TEXT,
        installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        configuration_notes TEXT,
        PRIMARY KEY (site_id, app_id),
        FOREIGN KEY (site_id) REFERENCES SITES (id),
        FOREIGN KEY (app_id) REFERENCES APPS (id)
    )
    ''')

    conn.commit()
    conn.close()
    logging.info("Database initialized successfully")

# CRUD operations for PROJECTS table
def create_project(name, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO PROJECTS (name, description)
        VALUES (?, ?)
        ''', (name, description))
        conn.commit()
        logging.info(f"Project '{name}' created successfully")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        logging.error(f"Project '{name}' already exists")
        return None
    finally:
        conn.close()

def get_project(project_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM PROJECTS WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    conn.close()
    return dict(project) if project else None

def update_project(project_id, name=None, description=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    update_fields = []
    update_values = []
    if name:
        update_fields.append('name = ?')
        update_values.append(name)
    if description:
        update_fields.append('description = ?')
        update_values.append(description)
    update_values.append(datetime.now())
    update_values.append(project_id)
    
    try:
        cursor.execute(f'''
        UPDATE PROJECTS
        SET {', '.join(update_fields)}, updated_at = ?
        WHERE id = ?
        ''', update_values)
        conn.commit()
        logging.info(f"Project {project_id} updated successfully")
        return True
    except sqlite3.Error as e:
        logging.error(f"Error updating project {project_id}: {e}")
        return False
    finally:
        conn.close()

def delete_project(project_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM PROJECTS WHERE id = ?', (project_id,))
        conn.commit()
        logging.info(f"Project {project_id} deleted successfully")
        return True
    except sqlite3.Error as e:
        logging.error(f"Error deleting project {project_id}: {e}")
        return False
    finally:
        conn.close()

# Similar CRUD operations should be implemented for other tables:
# CONTAINERS, INSTANCES, SITES, APPS, INSTANCE_APPS, and SITE_APPS

# Helper function to get all projects
def get_all_projects():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM PROJECTS')
    projects = cursor.fetchall()
    conn.close()
    return [dict(project) for project in projects]

# Initialize the database
init_db()

