# Application Data Model

This document defines a basic database schema for the internal storage needs of the schema generation application itself. This model is distinct from the database schemas that users will be creating using the application.

## I. Purpose

*   To store user account information, if user authentication is implemented.
*   To manage user-created projects, including their names, descriptions, and associations with users.
*   To store the various input sources (text, code, files) provided by users for each project.
*   To maintain versions or snapshots of the generated schemas for each project, allowing for history and potential rollback.
*   To store application-specific settings or preferences.

## II. Core Entities & Tables

### A. `Users` Table (Conditional: If user accounts are implemented)

*   **Purpose:** Stores information related to user accounts, supporting authentication and authorization.
*   **Columns:**
    *   `user_id` (Primary Key: UUID or SERIAL/BIGSERIAL for auto-incrementing INT) - Uniquely identifies a user.
    *   `username` (VARCHAR(255), UNIQUE, NULLABLE) - User-chosen unique username. Nullable if OAuth allows users without preset usernames initially or if email is the primary identifier.
    *   `email` (VARCHAR(255), UNIQUE, NOT NULL) - User's email address, used for login and communication.
    *   `password_hash` (VARCHAR(255), NULLABLE) - Hashed password for users registering with local authentication. Null if using only OAuth.
    *   `auth_provider` (VARCHAR(50), NULLABLE) - Indicates the authentication provider (e.g., 'local', 'google', 'github'). Null if only local auth.
    *   `auth_provider_id` (VARCHAR(255), NULLABLE) - Stores the unique user ID provided by the OAuth provider.
    *   `full_name` (VARCHAR(255), NULLABLE) - User's full name.
    *   `avatar_url` (TEXT, NULLABLE) - URL to the user's avatar image.
    *   `is_active` (BOOLEAN, NOT NULL, DEFAULT TRUE) - Whether the user account is active.
    *   `is_verified` (BOOLEAN, NOT NULL, DEFAULT FALSE) - Whether the user's email has been verified.
    *   `created_at` (TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT CURRENT_TIMESTAMP) - Timestamp of user creation.
    *   `updated_at` (TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT CURRENT_TIMESTAMP) - Timestamp of last update (trigger on update).
*   **Indexes:** `user_id` (PK), `email` (UNIQUE), `username` (UNIQUE, if not nullable), (`auth_provider`, `auth_provider_id`) (UNIQUE, if multiple OAuth providers).

### B. `Projects` Table

*   **Purpose:** Stores information about each schema design project created by a user.
*   **Columns:**
    *   `project_id` (Primary Key: UUID or SERIAL/BIGSERIAL) - Uniquely identifies a project.
    *   `user_id` (Foreign Key referencing `Users.user_id`, NULLABLE) - Associates the project with a user. Nullable if anonymous access/project creation is permitted.
    *   `project_name` (VARCHAR(255), NOT NULL) - User-defined name for the project.
    *   `description` (TEXT, NULLABLE) - A more detailed description of the project.
    *   `current_schema_version_id` (Foreign Key referencing `ProjectSchemaVersions.version_id`, NULLABLE) - Points to the currently active or latest version of the schema for this project.
    *   `created_at` (TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT CURRENT_TIMESTAMP) - Timestamp of project creation.
    *   `last_modified_at` (TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT CURRENT_TIMESTAMP) - Timestamp of the last modification to the project settings or its schema (trigger on update of project or related schema version).
*   **Indexes:** `project_id` (PK), `user_id`.

### C. `ProjectInputSources` Table

*   **Purpose:** Stores the various input sources (e.g., natural language text, SQL code snippets, uploaded files) provided by the user for a specific project. A project can be based on multiple input sources.
*   **Columns:**
    *   `input_id` (Primary Key: UUID or SERIAL/BIGSERIAL) - Uniquely identifies an input source.
    *   `project_id` (Foreign Key referencing `Projects.project_id`, NOT NULL) - Links the input to a project.
    *   `input_type` (VARCHAR(50), NOT NULL) - Type of input (e.g., 'natural_language', 'sql_snippet', 'python_orm', 'csv_file', 'json_file').
    *   `input_content` (TEXT, NULLABLE) - Stores text-based inputs like code snippets or natural language descriptions.
    *   `file_reference` (TEXT, NULLABLE) - For uploaded files, stores a reference (e.g., path on a file system, URL to blob storage, or an identifier for a managed file service).
    *   `original_file_name` (VARCHAR(255), NULLABLE) - The original name of an uploaded file.
    *   `file_size_bytes` (BIGINT, NULLABLE) - Size of the uploaded file.
    *   `metadata` (JSONB or TEXT, NULLABLE) - Stores additional metadata about the input (e.g., for code: {'language': 'python', 'orm': 'sqlalchemy'}; for CSV: {'delimiter': ',', 'has_header': true}).
    *   `status` (VARCHAR(50), NOT NULL, DEFAULT 'pending_processing') - Status of the input (e.g., 'pending_processing', 'processed', 'error').
    *   `created_at` (TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT CURRENT_TIMESTAMP) - Timestamp of input creation.
*   **Indexes:** `input_id` (PK), `project_id`.

### D. `ProjectSchemaVersions` Table

*   **Purpose:** Stores different versions or snapshots of the generated/refined schema for a project. This enables tracking history, comparing versions, and potentially rolling back to a previous schema state.
*   **Columns:**
    *   `version_id` (Primary Key: UUID or SERIAL/BIGSERIAL) - Uniquely identifies a schema version.
    *   `project_id` (Foreign Key referencing `Projects.project_id`, NOT NULL) - Links the schema version to a project.
    *   `version_number` (INTEGER, NOT NULL) - A sequential version number for the schema within a project (e.g., 1, 2, 3). Could be auto-incrementing per project or manually set.
    *   `schema_definition_ir` (JSONB or TEXT, NOT NULL) - Stores the application's internal, structured representation of the database schema at this version. This is the primary artifact.
    *   `based_on_input_ids` (JSONB or TEXT, NULLABLE) - An array or structured list of `input_id`s from `ProjectInputSources` that were used as the basis for generating or refining this schema version.
    *   `notes` (TEXT, NULLABLE) - User-provided notes or comments specific to this version of the schema (e.g., "Initial draft based on customer requirements doc", "Added auditing tables").
    *   `is_active_version` (BOOLEAN, DEFAULT FALSE) - A flag to quickly identify if this is the version currently linked from `Projects.current_schema_version_id`. (Alternatively, this can be solely managed by `Projects.current_schema_version_id`).
    *   `created_at` (TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT CURRENT_TIMESTAMP) - Timestamp of schema version creation.
*   **Indexes:** `version_id` (PK), `project_id`, (`project_id`, `version_number`) (UNIQUE constraint).

### E. `TargetDatabasePreferences` Table (Optional, for more advanced customization)

*   **Purpose:** Stores user-specific or project-specific preferences for generating schemas for particular target database systems, overriding application defaults.
*   **Columns:**
    *   `preference_id` (Primary Key: UUID or SERIAL/BIGSERIAL) - Uniquely identifies a preference set.
    *   `user_id` (Foreign Key referencing `Users.user_id`, NULLABLE) - If the preference is user-specific (applies to all their projects unless overridden).
    *   `project_id` (Foreign Key referencing `Projects.project_id`, NULLABLE) - If the preference is project-specific.
    *   `target_database_system` (VARCHAR(50), NOT NULL) - The target database system this preference applies to (e.g., 'MySQL', 'PostgreSQL', 'MongoDB').
    *   `preferences_json` (JSONB or TEXT, NOT NULL) - Stores the preference settings as a JSON object (e.g., `{"naming_convention": "snake_case", "default_varchar_length": 191, "use_uuid_pks": true}`).
    *   `created_at` (TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT CURRENT_TIMESTAMP)
    *   `updated_at` (TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT CURRENT_TIMESTAMP)
*   **Indexes:** `preference_id` (PK), (`user_id`, `target_database_system`) (UNIQUE), (`project_id`, `target_database_system`) (UNIQUE). A CHECK constraint might be needed to ensure either `user_id` or `project_id` is set, but not both if they are mutually exclusive levels.

## III. Relationships Summary

*   A `User` can have zero or more `Projects`.
*   A `Project` belongs to one `User` (or can be unassigned if anonymous access is allowed).
*   A `Project` can have one or more `ProjectInputSources` associated with it.
*   A `Project` can have one or more `ProjectSchemaVersions`, representing its history.
*   A `Project` typically has a `current_schema_version_id` that points to one specific entry in `ProjectSchemaVersions`, indicating the active schema.
*   `TargetDatabasePreferences` can be associated with a `User` (global for that user) or a `Project` (specific to that project), or neither (application-wide defaults, though these might be better handled in application configuration).

## IV. Data Types Considerations

*   **Primary Keys:** UUIDs are generally recommended for primary keys in distributed systems or if there's a need to generate IDs outside the database. Auto-incrementing integers (SERIAL/BIGSERIAL in PostgreSQL, AUTO_INCREMENT in MySQL) are simpler for smaller, single-database setups.
*   **JSONB/JSON:** Use `JSONB` in PostgreSQL for storing flexible, structured data like metadata or schema definitions, as it offers indexing capabilities. MySQL's `JSON` type provides similar benefits. For other databases, TEXT storing a JSON string is a fallback.
*   **Timestamps:** `TIMESTAMP WITH TIME ZONE` (TIMESTAMPTZ in PostgreSQL) is generally preferred over `TIMESTAMP WITHOUT TIME ZONE` to avoid ambiguity if the application or its users operate across different time zones. Store all timestamps in UTC.
*   **Foreign Keys:** Ensure `ON DELETE` and `ON UPDATE` actions are defined appropriately for foreign key constraints (e.g., `ON DELETE CASCADE` for `ProjectInputSources` if a `Project` is deleted, or `ON DELETE SET NULL` for `Projects.user_id` if a `User` is deleted but projects should be preserved as anonymous).

## V. Future Expansions

As the application evolves, other tables might be necessary:

*   `SharedProjects`: To manage sharing projects between different users with varying permission levels.
*   `SchemaTemplates`: To store predefined schema templates that users can start from.
*   `AuditLogs`: To track significant actions performed by users or by the system (e.g., project creation, schema export, user login).
*   `ApplicationSettings`: For global application configuration values that might need to be changed without code deployments.

This data model provides a foundational structure for the application's internal data management. It should be reviewed and refined as application requirements become more detailed.
