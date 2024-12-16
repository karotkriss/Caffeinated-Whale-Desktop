## Documentation for Frappe Docker CLI Tool

### Overview

The Frappe Docker CLI Tool is designed to manage and retrieve information about Frappe instances running in Docker containers. It utilizes a SQLite database to store project, container, site, and app information, allowing users to efficiently query and update their Frappe environments.

### Features

- **Database Initialization**: Automatically initializes a SQLite database to store project and container information.
- **Container Interaction**: Connects to Docker containers to find bench directories and list sites and apps.
- **Information Retrieval**: Provides commands to retrieve detailed information about projects, sites, and installed applications.

### Architecture

The tool is composed of three main scripts:

1. **Database Operations (`db_operations.py`)**: Handles database initialization, updates, and queries.
2. **Update Script (`update.py`)**: Interacts with Docker containers to update the database with current information about projects and their associated sites and apps.
3. **Info Retrieval Script (`info.py`)**: Provides a command-line interface for users to retrieve information about projects and sites.

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

To use the CLI tool, execute the `info.py` script with appropriate arguments. Below are some common commands:

1. **Get All Projects Information**

   ```bash
   python info.py
   ```

2. **Get Sites for a Specific Project**

   ```bash
   python info.py -p <project_name> --get-sites
   ```

3. **Get Installed Apps for a Specific Site**

   ```bash
   python info.py -p <project_name> --get-site-app <site_name>
   ```

4. **Get All Available Apps for a Project**

   ```bash
   python info.py -p <project_name> --get-apps
   ```

5. **Get Detailed Information for a Specific Site**

   ```bash
   python info.py -p <project_name> --get-site-info <site_name>
   ```

6. **Update Database Information**
   ```bash
   python update.py --project <project_name> --site <site_name> --bench --sites --apps
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
