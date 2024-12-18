import sqlite3
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database file path
DB_FILE = 'frappe_instances.db'

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
        bench_directory TEXT,
        db_root_password TEXT,
        status TEXT,
        version TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (container_id) REFERENCES CONTAINERS (id)
    )
    ''')

    # Create SITES table with updated schema including development_mode and db_type
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SITES (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        instance_id INTEGER,
        container_id INTEGER,
        name TEXT UNIQUE NOT NULL,
        domain TEXT UNIQUE NOT NULL,
        db_name TEXT UNIQUE NOT NULL,
        db_password TEXT NOT NULL,
        db_type TEXT,
        status TEXT,
        environment TEXT,
        development_mode INTEGER DEFAULT 0,
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

# CRUD operations for SITES table
def create_site(instance_id, container_id, name, domain, db_name, db_password, status, environment, development_mode=0, db_type=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO SITES (instance_id, container_id, name, domain, db_name, db_password, status, environment, development_mode, db_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (instance_id, container_id, name, domain, db_name, db_password, status, environment, development_mode, db_type))
        conn.commit()
        logging.info(f"Site '{name}' created successfully")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        logging.error(f"Site '{name}' already exists or db_name '{db_name}' is not unique")
        return None
    finally:
        conn.close()

def get_site(site_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM SITES WHERE id = ?', (site_id,))
    site = cursor.fetchone()
    conn.close()
    return dict(site) if site else None

def update_site(site_id, name=None, domain=None, db_name=None, db_password=None, status=None, environment=None, development_mode=None, db_type=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    update_fields = []
    update_values = []
    if name:
        update_fields.append('name = ?')
        update_values.append(name)
    if domain:
        update_fields.append('domain = ?')
        update_values.append(domain)
    if db_name:
        update_fields.append('db_name = ?')
        update_values.append(db_name)
    if db_password:
        update_fields.append('db_password = ?')
        update_values.append(db_password)
    if status:
        update_fields.append('status = ?')
        update_values.append(status)
    if environment:
        update_fields.append('environment = ?')
        update_values.append(environment)
    if development_mode is not None:
        update_fields.append('development_mode = ?')
        update_values.append(development_mode)
    if db_type:
        update_fields.append('db_type = ?')
        update_values.append(db_type)
    update_values.append(datetime.now())
    update_values.append(site_id)
    
    try:
        cursor.execute(f'''
        UPDATE SITES
        SET {', '.join(update_fields)}, updated_at = ?
        WHERE id = ?
        ''', update_values)
        conn.commit()
        logging.info(f"Site {site_id} updated successfully")
        return True
    except sqlite3.Error as e:
        logging.error(f"Error updating site {site_id}: {e}")
        return False
    finally:
        conn.close()

def delete_site(site_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM SITES WHERE id = ?', (site_id,))
        conn.commit()
        logging.info(f"Site {site_id} deleted successfully")
        return True
    except sqlite3.Error as e:
        logging.error(f"Error deleting site {site_id}: {e}")
        return False
    finally:
        conn.close()

def get_site_id(instance_id, site_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM SITES WHERE instance_id = ? AND name = ?', (instance_id, site_name))
    result = cursor.fetchone()
    conn.close()
    return result['id'] if result else None

def create_instance(container_id, name, bench_directory, status, version):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO INSTANCES (container_id, name, bench_directory, status, version)
        VALUES (?, ?, ?, ?, ?)
        ''', (container_id, name, bench_directory, status, version))
        conn.commit()
        logging.info(f"Instance '{name}' created successfully")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        logging.error(f"Instance '{name}' already exists")
        return None
    finally:
        conn.close()


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

def get_project(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM PROJECTS WHERE name = ?', (name,))
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

def create_container(project_id, container_id, container_type, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO CONTAINERS (project_id, container_id, container_type, status)
        VALUES (?, ?, ?, ?)
        ''', (project_id, container_id, container_type, status))
        conn.commit()
        logging.info(f"Container '{container_id}' created successfully")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        logging.error(f"Container '{container_id}' already exists")
        return None
    finally:
        conn.close()

def update_container(container_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        UPDATE CONTAINERS
        SET status = ?, updated_at = ?
        WHERE container_id = ?
        ''', (status, datetime.now(), container_id))
        conn.commit()
        logging.info(f"Container '{container_id}' updated successfully")
        return True
    except sqlite3.Error as e:
        logging.error(f"Error updating container '{container_id}': {e}")
        return False
    finally:
        conn.close()

def create_app(app_name, remote_url, version, category, released_at):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO APPS (app_name, remote_url, version, category, released_at)
        VALUES (?, ?, ?, ?, ?)
        ''', (app_name, remote_url, version, category, released_at))
        conn.commit()
        logging.info(f"App '{app_name}' created successfully")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        logging.error(f"App '{app_name}' already exists")
        return None
    finally:
        conn.close()

def create_instance_app(instance_id, app_id, version, status, install_method):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO INSTANCE_APPS (instance_id, app_id, version, status, install_method)
        VALUES (?, ?, ?, ?, ?)
        ''', (instance_id, app_id, version, status, install_method))
        conn.commit()
        logging.info(f"Instance app relation created successfully")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        logging.error(f"Instance app relation already exists")
        return None
    finally:
        conn.close()

def create_site_app(site_id, app_id, version, status, configuration_notes):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO SITE_APPS (site_id, app_id, version, status, configuration_notes)
        VALUES (?, ?, ?, ?, ?)
        ''', (site_id, app_id, version, status, configuration_notes))
        conn.commit()
        logging.info(f"Site app relation created successfully")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        logging.error(f"Site app relation already exists")
        return None
    finally:
        conn.close()

# Initialize the database
init_db()

def update_instance(instance_id, name=None, bench_directory=None, status=None, version=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    update_fields = []
    update_values = []
    if name:
        update_fields.append('name = ?')
        update_values.append(name)
    if bench_directory:
        update_fields.append('bench_directory = ?')
        update_values.append(bench_directory)
    if status:
        update_fields.append('status = ?')
        update_values.append(status)
    if version:
        update_fields.append('version = ?')
        update_values.append(version)
    update_values.append(datetime.now())
    update_values.append(instance_id)
    
    try:
        cursor.execute(f'''
        UPDATE INSTANCES
        SET {', '.join(update_fields)}, updated_at = ?
        WHERE id = ?
        ''', update_values)
        conn.commit()
        logging.info(f"Instance {instance_id} updated successfully")
        return True
    except sqlite3.Error as e:
        logging.error(f"Error updating instance {instance_id}: {e}")
        return False
    finally:
        conn.close()

# Initialize the database
init_db()

def create_or_update_project(name, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO PROJECTS (name, description)
        VALUES (?, ?)
        ON CONFLICT(name) DO UPDATE SET
        description = excluded.description,
        updated_at = CURRENT_TIMESTAMP
        ''', (name, description))
        conn.commit()
        logging.info(f"Project '{name}' created or updated successfully")
        return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Error creating or updating project '{name}': {e}")
        return None
    finally:
        conn.close()

def create_or_update_container(project_id, container_id, container_type, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO CONTAINERS (project_id, container_id, container_type, status)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(container_id) DO UPDATE SET
        project_id = excluded.project_id,
        container_type = excluded.container_type,
        status = excluded.status,
        updated_at = CURRENT_TIMESTAMP
        ''', (project_id, container_id, container_type, status))
        conn.commit()
        logging.info(f"Container '{container_id}' created or updated successfully")
        return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Error creating or updating container '{container_id}': {e}")
        return None
    finally:
        conn.close()

def create_or_update_instance(container_id, name, bench_directory, status, version):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO INSTANCES (container_id, name, bench_directory, status, version)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
        container_id = excluded.container_id,
        bench_directory = excluded.bench_directory,
        status = excluded.status,
        version = excluded.version,
        updated_at = CURRENT_TIMESTAMP
        ''', (container_id, name, bench_directory, status, version))
        conn.commit()
        logging.info(f"Instance '{name}' created or updated successfully")
        return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Error creating or updating instance '{name}': {e}")
        return None
    finally:
        conn.close()

def create_or_update_site(instance_id, container_id, name, domain, db_name, db_password, status, environment, development_mode=0, db_type=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO SITES (instance_id, container_id, name, domain, db_name, db_password, status, environment, development_mode, db_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
        domain = CASE WHEN instance_id = excluded.instance_id AND container_id = excluded.container_id THEN excluded.domain ELSE domain END,
        db_name = CASE WHEN instance_id = excluded.instance_id AND container_id = excluded.container_id THEN excluded.db_name ELSE db_name END,
        db_password = CASE WHEN instance_id = excluded.instance_id AND container_id = excluded.container_id THEN excluded.db_password ELSE db_password END,
        status = CASE WHEN instance_id = excluded.instance_id AND container_id = excluded.container_id THEN excluded.status ELSE status END,
        environment = CASE WHEN instance_id = excluded.instance_id AND container_id = excluded.container_id THEN excluded.environment ELSE environment END,
        development_mode = CASE WHEN instance_id = excluded.instance_id AND container_id = excluded.container_id THEN excluded.development_mode ELSE development_mode END,
        db_type = CASE WHEN instance_id = excluded.instance_id AND container_id = excluded.container_id THEN excluded.db_type ELSE db_type END,
        updated_at = CURRENT_TIMESTAMP
        WHERE instance_id = excluded.instance_id AND container_id = excluded.container_id
        ''', (instance_id, container_id, name, domain, db_name, db_password, status, environment, development_mode, db_type))
        conn.commit()
        logging.info(f"Site '{name}' created or updated successfully")
        return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Error creating or updating site '{name}': {e}")
        return None
    finally:
        conn.close()

def create_or_update_app(app_name, remote_url, version, category, released_at):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO APPS (app_name, remote_url, version, category, released_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(app_name) DO UPDATE SET
        remote_url = excluded.remote_url,
        version = excluded.version,
        category = excluded.category,
        released_at = excluded.released_at
        ''', (app_name, remote_url, version, category, released_at))
        conn.commit()
        logging.info(f"App '{app_name}' created or updated successfully")
        return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Error creating or updating app '{app_name}': {e}")
        return None
    finally:
        conn.close()

def create_or_update_instance_app(instance_id, app_id, version, status, install_method):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO INSTANCE_APPS (instance_id, app_id, version, status, install_method)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(instance_id, app_id) DO UPDATE SET
        version = excluded.version,
        status = excluded.status,
        install_method = excluded.install_method,
        installed_at = CURRENT_TIMESTAMP
        ''', (instance_id, app_id, version, status, install_method))
        conn.commit()
        logging.info(f"Instance app relation created or updated successfully")
        return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Error creating or updating instance app relation: {e}")
        return None
    finally:
        conn.close()

