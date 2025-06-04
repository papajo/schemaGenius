# Export Formats and Options

## 1. Introduction

### Purpose of Export Functionality
The export functionality allows users to take the database schema they have designed or generated within the application and use it in their target environments. This includes deploying it to a live database, sharing it with team members, using it for documentation, or integrating it with other development tools.

### Goal
The primary goal is to provide users with flexible and usable export formats that are compatible with common database systems and data interchange standards. The exported output should be accurate, complete, and easy to use.

## 2. Supported Export Formats

### A. SQL Data Definition Language (DDL)

*   **Description:** Generates SQL statements required to create the database structure (tables, columns, constraints, indexes) in a relational database.
*   **Target Databases (Initially):**
    *   MySQL
    *   PostgreSQL
    *   (Potential future expansion: SQLite, SQL Server, Oracle)
*   **Content:**
    *   **Table Creation:** `CREATE TABLE` statements for each table defined in the schema.
    *   **Column Definitions:** Each column defined with its name, target database-specific data type (e.g., `VARCHAR(255)`, `INT`, `TEXT`), `NOT NULL` constraints, and `DEFAULT` values if specified.
    *   **Primary Key Constraints:** Defined either inline with column definition or as a separate `PRIMARY KEY (...)` clause or using `ALTER TABLE ... ADD CONSTRAINT ... PRIMARY KEY ...`.
    *   **Foreign Key Constraints:** `FOREIGN KEY (...) REFERENCES ... (...)` clauses, potentially with `ON DELETE` and `ON UPDATE` actions (e.g., `CASCADE`, `SET NULL`, `RESTRICT`). Typically added via `ALTER TABLE` to avoid order-of-creation issues.
    *   **Unique Constraints:** `UNIQUE` constraints for specified columns.
    *   **Check Constraints:** `CHECK (...)` constraints if defined by the user and supported by the target database.
    *   **Index Definitions:** `CREATE INDEX` statements for any custom indexes defined on tables.
    *   **Optional `DROP TABLE IF EXISTS ...` Statements:** (User-selectable option) Prepends `DROP TABLE IF EXISTS table_name;` for each table, allowing the script to be run multiple times safely.
    *   **Optional Comments:** (User-selectable option) Table and column comments using `COMMENT ON TABLE ... IS '...'` or inline syntax if supported by the target RDBMS (e.g., MySQL's `COMMENT '...'` in `CREATE TABLE`).
*   **MySQL Specifics:**
    *   **Storage Engine:** Option to specify `ENGINE=InnoDB` (or other engines, though InnoDB is typical).
    *   **Character Set and Collation:** Option to specify default character set and collation for tables, e.g., `DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci`.
    *   **Auto Increment:** `AUTO_INCREMENT` keyword for primary keys.
    *   **Identifier Quoting:** Backticks for identifiers (e.g., `` `table_name` ``).
*   **PostgreSQL Specifics:**
    *   **Schema Support:** Table names can be schema-qualified (e.g., `CREATE TABLE public.my_table ...`). Defaults to `public` if not specified.
    *   **Auto Increment:** Use of `SERIAL`, `BIGSERIAL` pseudo-types, or `GENERATED AS IDENTITY` for auto-incrementing primary keys.
    *   **Identifier Quoting:** Double quotes for identifiers if they contain special characters or are case-sensitive (e.g., `"MyTable"`).
*   **Example Snippet (Conceptual for MySQL):**
    ```sql
    -- Exported from SchemaGenius
    -- Project: MyBlog
    -- Target: MySQL 8.0
    -- Timestamp: 2023-11-15_10-30-00

    SET FOREIGN_KEY_CHECKS=0; -- Optional: to handle inter-dependencies during drop/create

    DROP TABLE IF EXISTS `posts`;
    DROP TABLE IF EXISTS `users`;

    SET FOREIGN_KEY_CHECKS=1; -- Re-enable checks

    -- Table structure for table `users`
    CREATE TABLE `users` (
        `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique identifier for the user',
        `username` VARCHAR(100) NOT NULL UNIQUE,
        `email` VARCHAR(255) NOT NULL UNIQUE,
        `full_name` VARCHAR(200) NULL,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT 'Stores user account information';

    -- Table structure for table `posts`
    CREATE TABLE `posts` (
        `id` INT AUTO_INCREMENT PRIMARY KEY,
        `title` VARCHAR(255) NOT NULL,
        `content` TEXT,
        `user_id` INT NOT NULL,
        `published_at` DATETIME NULL,
        CONSTRAINT `fk_posts_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT 'Stores blog posts authored by users';

    -- Indexes for table `posts`
    CREATE INDEX `idx_posts_user_id` ON `posts` (`user_id`);
    CREATE INDEX `idx_posts_published_at` ON `posts` (`published_at`);
    ```

### B. JSON Schema Representation

*   **Purpose:** Provides a machine-readable format for the database schema. Useful for:
    *   Integration with other applications or scripts.
    *   Programmatic validation or manipulation of schema definitions.
    *   Serving as an intermediate, standardized format for documentation or conversion to other formats.
    *   Potentially for use with MongoDB's JSON Schema validation.
*   **Structure:** A single JSON object representing the entire database schema. The structure will be well-defined, potentially similar to the application's internal intermediate schema representation but finalized and cleaned for export.
*   **Key Elements:**
    *   `schemaName`: Name of the project or schema.
    *   `version`: Version of the schema (if applicable).
    *   `exportedAt`: ISO 8601 timestamp of the export.
    *   `targetDatabase`: (Optional) The database system this schema was intended for (e.g., "PostgreSQL", "Generic").
    *   `tables`: An array of objects, where each object represents a table (or collection for NoSQL).
        *   `name`: Name of the table.
        *   `comment`: (Optional) Description of the table.
        *   `columns`: An array of objects, each representing a column/field.
            *   `name`: Name of the column.
            *   `type`: Data type (can be generic like "STRING", "INTEGER", "BOOLEAN", or target-specific like "VARCHAR(255)", "SERIAL").
            *   `isNullable`: Boolean (true if nullable, false if NOT NULL).
            *   `isPrimaryKey`: Boolean.
            *   `isUnique`: Boolean.
            *   `autoIncrement`: Boolean (if applicable).
            *   `defaultValue`: The default value as a string or appropriate type.
            *   `comment`: (Optional) Description of the column.
            *   (Other type-specific attributes like `maxLength`, `precision`, `scale` for strings/decimals).
        *   `primaryKey`: (Optional) An object or array defining the primary key columns.
        *   `foreignKeys`: An array of objects, each defining a foreign key.
            *   `name`: (Optional) Constraint name.
            *   `columns`: Array of column names in the current table.
            *   `referencesTable`: Name of the referenced table.
            *   `referencesColumns`: Array of column names in the referenced table.
            *   `onDelete`: (Optional) Action like "CASCADE", "SET NULL", "RESTRICT".
            *   `onUpdate`: (Optional) Action.
        *   `indexes`: An array of objects, each defining an index.
            *   `name`: Name of the index.
            *   `columns`: Array of column names included in the index.
            *   `isUnique`: Boolean.
            *   `type`: (Optional) Index type (e.g., "BTREE", "HASH").
*   **Example Snippet (Conceptual):**
    ```json
    {
      "schemaName": "MyBlogSchema",
      "version": "1.0.0",
      "exportedAt": "2023-11-15T10:30:00Z",
      "targetDatabase": "MySQL",
      "tables": [
        {
          "name": "users",
          "comment": "Stores user account information",
          "columns": [
            {"name": "id", "type": "INT", "isNullable": false, "isPrimaryKey": true, "autoIncrement": true, "comment": "Unique identifier for the user"},
            {"name": "username", "type": "VARCHAR(100)", "isNullable": false, "isUnique": true},
            {"name": "email", "type": "VARCHAR(255)", "isNullable": false, "isUnique": true},
            {"name": "full_name", "type": "VARCHAR(200)", "isNullable": true},
            {"name": "created_at", "type": "TIMESTAMP", "isNullable": true, "defaultValue": "CURRENT_TIMESTAMP"}
          ],
          "primaryKey": {"columns": ["id"]}
        },
        {
          "name": "posts",
          "comment": "Stores blog posts authored by users",
          "columns": [
            {"name": "id", "type": "INT", "isNullable": false, "isPrimaryKey": true, "autoIncrement": true},
            {"name": "title", "type": "VARCHAR(255)", "isNullable": false},
            {"name": "content", "type": "TEXT", "isNullable": true},
            {"name": "user_id", "type": "INT", "isNullable": false},
            {"name": "published_at", "type": "DATETIME", "isNullable": true}
          ],
          "primaryKey": {"columns": ["id"]},
          "foreignKeys": [
            {
              "name": "fk_posts_user_id",
              "columns": ["user_id"],
              "referencesTable": "users",
              "referencesColumns": ["id"],
              "onDelete": "CASCADE",
              "onUpdate": "NO ACTION"
            }
          ],
          "indexes": [
            {"name": "idx_posts_user_id", "columns": ["user_id"], "isUnique": false},
            {"name": "idx_posts_published_at", "columns": ["published_at"], "isUnique": false}
          ]
        }
      ]
    }
    ```

### C. XML Schema Representation

*   **Purpose:** For integration with systems that primarily use XML, such as some enterprise applications, SOAP-based web services, or for specific documentation requirements.
*   **Structure:** An XML document representing the schema. Initially, a custom XML structure will be used for simplicity. In the future, adherence to a standard like XSD (XML Schema Definition) could be an option for broader compatibility, though XSD itself is primarily for defining the structure *of* XML documents, not necessarily database schemas directly.
*   **Key Elements (Custom XML):** Analogous to the JSON structure.
    *   Root element: `<databaseSchema name="MyBlogSchema" version="1.0.0" exportedAt="2023-11-15T10:30:00Z" targetDatabase="MySQL">`
    *   Table elements: `<table name="users" comment="Stores user information">`
    *   Column elements: `<column name="id" type="INT" isNullable="false" isPrimaryKey="true" autoIncrement="true" comment="Unique identifier for the user"/>`
    *   Constraints within table or column elements or as separate elements:
        *   `<primaryKey><columnRef name="id"/></primaryKey>`
        *   `<foreignKey name="fk_posts_user_id" onDelete="CASCADE" onUpdate="NO_ACTION"> <columnRef name="user_id"/> <references table="users"> <columnRef name="id"/> </references> </foreignKey>`
        *   `<index name="idx_posts_user_id"><columnRef name="user_id"/></index>`
*   **Example Snippet (Conceptual - Custom XML):**
    ```xml
    <?xml version="1.0" encoding="UTF-8"?>
    <!--
      Exported from SchemaGenius
      Project: MyBlog
      Target: MySQL 8.0
      Timestamp: 2023-11-15_10-30-00
    -->
    <databaseSchema name="MyBlogSchema" version="1.0.0" exportedAt="2023-11-15T10:30:00Z" targetDatabase="MySQL">
        <table name="users" comment="Stores user account information">
            <column name="id" type="INT" isNullable="false" isPrimaryKey="true" autoIncrement="true" comment="Unique identifier for the user"/>
            <column name="username" type="VARCHAR(100)" isNullable="false" isUnique="true"/>
            <column name="email" type="VARCHAR(255)" isNullable="false" isUnique="true"/>
            <column name="full_name" type="VARCHAR(200)" isNullable="true"/>
            <column name="created_at" type="TIMESTAMP" isNullable="true" defaultValue="CURRENT_TIMESTAMP"/>
            <primaryKey>
                <columnRef name="id"/>
            </primaryKey>
        </table>
        <table name="posts" comment="Stores blog posts authored by users">
            <column name="id" type="INT" isNullable="false" isPrimaryKey="true" autoIncrement="true"/>
            <column name="title" type="VARCHAR(255)" isNullable="false"/>
            <column name="content" type="TEXT" isNullable="true"/>
            <column name="user_id" type="INT" isNullable="false"/>
            <column name="published_at" type="DATETIME" isNullable="true"/>
            <primaryKey>
                <columnRef name="id"/>
            </primaryKey>
            <foreignKeys>
                <foreignKey name="fk_posts_user_id" onDelete="CASCADE" onUpdate="NO_ACTION">
                    <columnRef name="user_id"/>
                    <references table="users">
                        <columnRef name="id"/>
                    </references>
                </foreignKey>
            </foreignKeys>
            <indexes>
                <index name="idx_posts_user_id">
                    <columnRef name="user_id"/>
                </index>
                <index name="idx_posts_published_at">
                    <columnRef name="published_at"/>
                </index>
            </indexes>
        </table>
    </databaseSchema>
    ```

## 3. Export Options (User-Selectable in UI)

These options will be presented to the user in the "Export Schema" modal/page to customize the output.

*   **Target Database (Mainly for SQL DDL):**
    *   UI: Dropdown list.
    *   Options: "MySQL", "PostgreSQL". (More can be added later).
    *   Effect: Determines SQL dialect, data type mappings, and supported features in the DDL output. For JSON/XML, this might influence the `targetDatabase` metadata field.
*   **Include `DROP TABLE IF EXISTS` statements (SQL DDL):**
    *   UI: Checkbox.
    *   Default: Checked.
    *   Effect: If checked, each `CREATE TABLE` statement will be preceded by a corresponding `DROP TABLE IF EXISTS table_name;` statement.
*   **Include Comments (SQL DDL, JSON, XML):**
    *   UI: Checkbox.
    *   Default: Checked.
    *   Effect: If checked, any descriptions or comments added by the user to tables and columns within the schema editor will be included in the exported file (e.g., as SQL `COMMENT` statements or `comment` fields in JSON/XML).
*   **Naming Convention for Export (Advanced - Future Enhancement):**
    *   UI: Dropdown list (e.g., "Keep as defined", "Convert to snake_case", "Convert to camelCase", "Convert to PascalCase").
    *   Default: "Keep as defined".
    *   Effect: Transforms the names of tables and columns in the exported output according to the selected convention.
*   **Character Set/Collation (for MySQL DDL - Future Enhancement):**
    *   UI: Dropdown lists for default character set and collation.
    *   Default: Sensible defaults (e.g., `utf8mb4`, `utf8mb4_unicode_ci`).
    *   Effect: Sets the default character set and collation for `CREATE TABLE` statements in MySQL DDL.

## 4. File Naming Convention for Downloads

Exported files will be named consistently to help users manage them:

*   SQL DDL: `{project_name}_{target_db}_{timestamp}.sql` (e.g., `MyBlog_MySQL_20231115103000.sql`)
*   JSON Schema: `{project_name}_{timestamp}.json` (e.g., `MyBlog_20231115103000.json`)
*   XML Schema: `{project_name}_{timestamp}.xml` (e.g., `MyBlog_20231115103000.xml`)

Where:
*   `{project_name}` is the user-defined name of the project (sanitized for use in filenames).
*   `{target_db}` is a short identifier for the database (e.g., `mysql`, `pgsql`).
*   `{timestamp}` is a compact representation of the export date and time (e.g., `YYYYMMDDHHMMSS`).
