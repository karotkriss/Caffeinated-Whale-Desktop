## Documentation for Frappe Docker CLI Tool

### Overview
The Frappe Docker CLI Tool is designed to manage and retrieve information about Frappe instances running in Docker containers. It utilizes a SQLite database to store project, container, site, and app information, allowing users to efficiently query and update their Frappe environments.

### Features
- **Database Initialization**: Automatically initializes a SQLite database to store project and container information.
- **Container Interaction**: Connects to Docker containers to find bench directories and list sites and apps.
- **Information Retrieval**: Provides commands to retrieve detailed information about projects, sites, and installed applications.

### Architecture
The tool is composed of three main scripts:
1. **Database Operations (`backend/db_operations.py`)**: Handles database initialization, updates, and queries.
2. **Update Script (`backend/update_db.py`)**: Interacts with Docker containers to update the database with current information about projects and their associated sites and apps.
3. **Info Retrieval Script (`backend/frappe_instance_info.py`)**: Provides a command-line interface for users to retrieve information about projects and sites.

### Database Schema

The SQLite database consists of the following tables:

#### Projects Table

| Column | Type                 | Description                        |
| ------ | -------------------- | ---------------------------------- |
| id     | INTEGER PRIMARY KEY  | Unique identifier for each project |
| name   | TEXT UNIQUE NOT NULL | Name of the project                |

#### Containers Table

| Column       | Type                 | Description                               |
| ------------ | -------------------- | ----------------------------------------- |
| id           | INTEGER PRIMARY KEY  | Unique identifier for each container      |
| project_id   | INTEGER              | Foreign key linking to the projects table |
| container_id | TEXT UNIQUE NOT NULL | Unique identifier for the container       |
| bench_dir    | TEXT                 | Path to the bench directory               |

#### Sites Table

| Column       | Type                | Description                                 |
| ------------ | ------------------- | ------------------------------------------- |
| id           | INTEGER PRIMARY KEY | Unique identifier for each site             |
| container_id | INTEGER             | Foreign key linking to the containers table |
| name         | TEXT NOT NULL       | Name of the site                            |

#### Apps Table

| Column       | Type                | Description                                 |
| ------------ | ------------------- | ------------------------------------------- |
| id           | INTEGER PRIMARY KEY | Unique identifier for each app              |
| container_id | INTEGER             | Foreign key linking to the containers table |
| name         | TEXT NOT NULL       | Name of the app                             |

### Usage Instructions

#### Command-Line Interface (CLI)

##### Update Database Information
To update Frappe instance information in the database, execute the `backend/update_db.py` script with appropriate arguments:

```bash
python backend/update_db.py [-h] [-p PROJECT] [-s SITE] [--bench] [--sites] [--apps] [--all]
```

**Options:**
- `-h, --help`: Show help message and exit.
- `-p PROJECT, --project PROJECT`: Docker Compose project name to update (default: update all projects).
- `-s SITE, --site SITE`: Specific site to update within a project.
- `--bench`: Update bench directory information.
- `--sites`: Update sites information.
- `--apps`: Update available apps information.
- `--all`: Update all information (default if no specific update is selected).

**Usage Examples:**
- Update all projects:
  ```bash
  python backend/update_db.py --all
  ```

- Update a specific project:
  ```bash
  python backend/update_db.py -p my_project --bench --sites --apps
  ```

- Update a specific site within a project:
  ```bash
  python backend/update_db.py -p my_project -s my_site --apps
  ```

##### Retrieve Frappe Instance Information
To retrieve information about Frappe instances, execute the `backend/frappe_instance_info.py` script with appropriate arguments:

```bash
python backend/frappe_instance_info.py [-h] [-p PROJECT] [--get-sites | --get-site-app SITE | --get-apps | --get-site-info SITE]
```

**Options:**
- `-h, --help`: Show help message and exit.
- `-p PROJECT, --project PROJECT`: Docker Compose project name.
- `--get-sites`: Get all sites for the project.
- `--get-site-app SITE`: Get installed apps for a specific site.
- `--get-apps`: Get all available apps for the project.
- `--get-site-info SITE`: Get detailed information for a specific site.

**Usage Examples:**
- Get all projects' information:
  ```bash
  python backend/frappe_instance_info.py
  ```

- Get all sites for a specific project:
  ```bash
  python backend/frappe_instance_info.py -p my_project --get-sites
  ```

- Get installed apps for a specific site:
  ```bash
  python backend/frappe_instance_info.py -p my_project --get-site-app my_site
  ```

- Get all available apps for a project:
  ```bash
  python backend/frappe_instance_info.py -p my_project --get-apps
  ```

- Get detailed information for a specific site:
  ```bash
  python backend/frappe_instance_info.py -p my_project --get-site-info my_site
  ```

### Diagrams

#### System Architecture Diagram

```plaintext
+-------------------+
|                   |
|  Frappe Docker    |
|     Containers    |
|                   |
+---------+---------+
          |
          v
+---------+---------+
|                   |
|  CLI Tool         |
|                   |
+---------+---------+
          |
          v
+---------+---------+
|                   |
|  SQLite Database  |
|                   |
+-------------------+
```

#### Database Schema Diagram

```plaintext
+-------------------+
|     Projects      |
+-------------------+
| id (PK)           |
| name              |
+-------------------+
         |
         v
+-------------------+
|    Containers     |
+-------------------+
| id (PK)           |
| project_id (FK)   |
| container_id      |
| bench_dir         |
+-------------------+
         |
         v
+-------------------+
|       Sites       |
+-------------------+
| id (PK)           |
| container_id (FK)  |
| name              |
+-------------------+
         ^
         |
+-------------------+
|       Apps        |
+-------------------+
| id (PK)           |
| container_id (FK)  |
| name              |
+-------------------+
```
