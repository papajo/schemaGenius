# Parsing and Analysis Engine: Detailed Description

## 1. Overview

The Parsing and Analysis Engine is the intellectual core of the Automatic Database Schema Generation application. Its primary role is to transform diverse user inputs—ranging from structured SQL Data Definition Language (DDL) and Object-Relational Mapper (ORM) code to less structured natural language descriptions and data files—into a concrete database schema.

The engine is designed with modularity at its heart. This allows for the independent development, testing, and enhancement of individual parsing components and enables the system to be easily extended to support new input formats or target database systems in the future.

## 2. Input Processing Pipeline (Conceptual)

The journey from raw user input to a generated database schema follows a conceptual pipeline within the engine:

1.  **Input Reception:** The engine receives input data and associated parameters (e.g., desired target database type) from the Backend API. This input could be a file upload, a snippet of code, or plain text.
2.  **Input Type Identification:** The engine (or the Backend API before dispatching) attempts to identify the type of input (e.g., SQL DDL, Python code, CSV file, natural language text). This might involve inspecting file extensions, content sniffing, or explicit user selection.
3.  **Delegation to Specific Parser:** Based on the identified input type, the task is delegated to the appropriate parser module (e.g., SQL Parser, Python ORM Parser, NLP Engine).
4.  **Parsing and AST/Structure Generation:** The selected parser analyzes the input and converts it into a structured, often abstract, representation. For code, this is typically an Abstract Syntax Tree (AST); for text, it's a set of identified entities and relationships; for data files, it's an inferred structure.
5.  **Normalization to Intermediate Schema Representation:** The output from the specific parser is transformed into a common, generalized format known as the Intermediate Schema Representation. This canonical form is crucial for decoupling the parsing logic from the final database-specific generation logic.
6.  **Refinement & Enrichment:** The Intermediate Schema may undergo further processing. This stage can involve:
    *   Applying heuristics to infer missing information (e.g., suggesting primary keys, inferring data types from column names like `is_active` -> BOOLEAN).
    *   Inferring relationships that were not explicitly stated but are implied by naming conventions (e.g., a `user_id` column in a `orders` table likely links to an `id` column in a `users` table).
    *   Validating the consistency of the schema.
7.  **Conversion to Target Database Schema (via Adapters):** Finally, the refined Intermediate Schema Representation is passed to a Database-Specific Adapter. This adapter translates the generic schema into the specific DDL statements or schema definitions required by the user's chosen target database system (e.g., MySQL, PostgreSQL, MongoDB).

## 3. Parsers

### 3.1. SQL Parser
*   **Input:** SQL DDL statements (e.g., `CREATE TABLE`, `ALTER TABLE`, `CREATE INDEX`).
*   **Technology/Library:**
    *   **Primary:** ANTLR with existing, well-tested SQL grammars (e.g., GenericSQL, or specific grammars for T-SQL, PL/pgSQL if available and robust). ANTLR provides the capability to generate a parser from a grammar that can produce a detailed AST.
    *   **Secondary/Helper:** Python libraries like `sqlparse` can be used for simpler tasks like SQL splitting, basic validation, or extracting comments, but may not be sufficient for full, accurate DDL interpretation across dialects.
*   **Output:** An AST or a structured representation detailing:
    *   Tables: Names, schemas (if applicable).
    *   Columns: Names, data types (e.g., `VARCHAR(255)`, `INT`, `TIMESTAMP`), default values.
    *   Constraints: `PRIMARY KEY`, `FOREIGN KEY` (including referenced table and columns), `UNIQUE`, `NOT NULL`, `CHECK` constraints.
    *   Indexes: Names, indexed columns, uniqueness.
*   **Details:**
    *   **Dialect Handling:** SQL dialects (MySQL, PostgreSQL, SQL Server, Oracle, etc.) have variations in syntax for DDL. The parser must be robust to these differences. This might involve:
        *   Using a sufficiently generic grammar that covers common DDL.
        *   Having dialect-specific grammars or post-processing rules for the AST.
        *   Initially focusing on the most common constructs for selected dialects (e.g., MySQL and PostgreSQL).
    *   **Error Handling:** Gracefully handle syntax errors in the input SQL and provide meaningful feedback.

### 3.2. Code Parsers (Python ORM, Java JPA/Hibernate)
*   **Input:**
    *   Python: `.py` files containing class definitions using SQLAlchemy or Django ORM.
    *   Java: `.java` files containing entity class definitions using JPA (e.g., `@Entity`) or Hibernate annotations.
*   **Technology/Library:**
    *   **Python ORM:**
        *   Python's built-in `ast` module to parse Python source code into an AST.
        *   Custom visitor classes to traverse the AST, identify ORM model class definitions (e.g., classes inheriting from `db.Model` in Flask-SQLAlchemy or `models.Model` in Django).
        *   Logic to extract table names (often derived from class names), column names (from class attributes), data types (from ORM field types like `db.Column(db.String)`) and relationships (e.g., `db.relationship`, `models.ForeignKey`).
    *   **Java JPA/Hibernate:**
        *   **JavaParser** library (or similar like Eclipse JDT) to parse Java source code into an AST.
        *   Logic to identify classes annotated with `@Entity`.
        *   Extract table names (from `@Table` annotation or class name).
        *   Extract column information from fields annotated with `@Column`, `@Id`.
        *   Extract relationships from annotations like `@OneToOne`, `@OneToMany`, `@ManyToOne`, `@ManyToMany`.
*   **Output:** A structured representation similar to that produced by the SQL parser (tables, columns, data types, relationships/foreign keys).

### 3.3. Natural Language Processor (NLP)
*   **Input:** Textual descriptions provided by the user, outlining their database requirements.
    *   Example: "I need a system to track authors and their books. An author has a name and biography. A book has a title, ISBN, and publication year. An author can write many books."
*   **Technology/Library:** Python with **spaCy** for its robustness and extensive features. NLTK is an alternative.
*   **Process:**
    1.  **Text Preprocessing:**
        *   Tokenization: Breaking text into words and sentences.
        *   Lemmatization: Reducing words to their base or dictionary form.
        *   Stop Word Removal: Eliminating common words (e.g., "the", "is", "a") that add little semantic meaning for schema generation.
        *   Part-of-Speech (POS) Tagging: Identifying nouns, verbs, adjectives, etc.
    2.  **Entity Recognition (Table & Column Identification):**
        *   Utilize spaCy's Named Entity Recognition (NER) capabilities. Nouns and noun phrases are strong candidates for table and column names.
        *   Develop rule-based patterns (e.g., using spaCy's `Matcher` or `PhraseMatcher`) to identify constructs like "a table for X", "X has fields Y, Z".
        *   Custom training of NER models could be a future enhancement for domain-specific terms.
    3.  **Relationship Extraction:**
        *   Analyze verb phrases and prepositions connecting identified entities (e.g., "author *can write* many books", "books *belong to* an author").
        *   Use spaCy's dependency parser to understand grammatical relationships between words.
        *   Rule-based patterns to map linguistic structures to relationship types (one-to-one, one-to-many, many-to-many).
        *   Keywords like "has a", "contains", "many", "multiple" can indicate relationships.
    4.  **Data Type Inference:**
        *   Apply heuristics based on keywords in the description (e.g., "text description" -> TEXT, "unique identifier" -> INTEGER/UUID, "start date" -> DATE).
        *   Infer types from common field names (e.g., `email` -> STRING, `age` -> INTEGER, `is_deleted` -> BOOLEAN).
        *   This stage is inherently fuzzy and may require user confirmation.
*   **Output:** A structured representation of potential tables, columns (with probable data types), and relationships. This output is expected to be less precise than that from structured inputs and will likely serve as a starting point requiring user validation and refinement.

### 3.4. File Parsers (CSV, JSON)
*   **Input:**
    *   CSV: Comma-Separated Values files, typically with a header row.
    *   JSON: Files containing an array of objects (where each object represents a row and keys are column names) or a single object whose keys are table names and values describe table structures.
*   **Technology/Library:**
    *   Python's built-in `csv` module for CSV parsing.
    *   Python's built-in `json` module for JSON parsing.
*   **Process:**
    *   **CSV:**
        *   Read the header row to determine column names. If no header, generate default names (e.g., `column_1`, `column_2`).
        *   Infer data types by sampling a configurable number of rows. For each column, analyze the data:
            *   If all values parse as integers -> INTEGER.
            *   If all values parse as numbers (int or float) -> DECIMAL/FLOAT.
            *   If all values parse as dates/datetimes -> DATE/DATETIME.
            *   If values are consistently true/false/0/1 -> BOOLEAN.
            *   Otherwise -> STRING/TEXT.
        *   Consider maximum string length observed for VARCHAR type sizing.
    *   **JSON:**
        *   If an array of objects: Use the keys from the first object as column names. Infer data types by inspecting values from multiple objects, similar to CSV.
        *   If a single object representing table structures (less common for raw data input, more for schema description): Parse the predefined structure.
*   **Output:** Structured representation of one or more tables, columns, and inferred data types.

## 4. Intermediate Schema Representation

*   **Purpose:** To provide a standardized, database-agnostic format for representing the schema within the engine. This decouples the initial parsing phase from the final database-specific generation phase, promoting modularity and simplifying the addition of new parsers or target database adapters.
*   **Structure:** A collection of Python objects or a nested dictionary structure. Key elements include:
    *   **Tables:** Each table defined by its name and a list of columns and other properties.
    *   **Columns:** Each column defined by its name, a generic data type, and properties like `is_primary_key`, `is_unique`, `is_nullable`, `default_value`.
    *   **Generic Data Types:** A limited set of abstract types like `STRING`, `TEXT`, `INTEGER`, `DECIMAL(precision, scale)`, `BOOLEAN`, `DATE`, `DATETIME`, `BLOB`, `JSON_TYPE`, `UUID_TYPE`, `ENUM_TYPE(values)`.
    *   **Relationships (Foreign Keys):** Defined by the source column(s) in the current table, the target table name, and the target column(s) in the referenced table. Also, cardinality (one-to-one, one-to-many) if inferred.
    *   **Indexes:** Defined by name, type (e.g., BTREE, HASH), uniqueness, and the list of columns they cover.
    *   **Constraints:** Other constraints like `CHECK` constraints.
*   **Example (JSON-like structure):**
    ```json
    {
      "schema_name": "my_database_schema",
      "tables": [
        {
          "name": "users",
          "columns": [
            {"name": "id", "type": "INTEGER", "is_primary_key": true, "auto_increment": true},
            {"name": "username", "type": "STRING", "length": 50, "is_unique": true, "is_nullable": false},
            {"name": "email", "type": "STRING", "length": 255, "is_unique": true, "is_nullable": false},
            {"name": "created_at", "type": "DATETIME", "default_value": "CURRENT_TIMESTAMP"}
          ],
          "indexes": [
            {"name": "idx_username", "columns": ["username"], "is_unique": true}
          ]
        },
        {
          "name": "posts",
          "columns": [
            {"name": "id", "type": "INTEGER", "is_primary_key": true, "auto_increment": true},
            {"name": "title", "type": "STRING", "length": 200, "is_nullable": false},
            {"name": "content", "type": "TEXT", "is_nullable": true},
            {"name": "author_id", "type": "INTEGER", "is_nullable": false},
            {"name": "published_at", "type": "DATETIME", "is_nullable": true}
          ],
          "foreign_keys": [
            {
              "name": "fk_post_author",
              "columns": ["author_id"],
              "references_table": "users",
              "references_columns": ["id"],
              "on_delete": "CASCADE",
              "on_update": "NO ACTION"
            }
          ]
        }
      ]
    }
    ```

## 5. Schema Inference and Enrichment Logic

After initial parsing into the Intermediate Schema Representation, this stage applies further logic to refine and complete the schema:

*   **Data Type Heuristics:**
    *   If data types are ambiguous or not provided (especially from NLP or CSV without explicit typing), suggest types based on column names (e.g., `is_`, `has_` prefixes -> BOOLEAN; `_at`, `_date` suffixes -> DATETIME/DATE; `email` -> STRING; `phone` -> STRING; `price`, `amount` -> DECIMAL).
*   **Primary Key (PK) Generation:**
    *   If a table lacks a defined primary key, automatically add an `id` column (e.g., INTEGER with auto-increment or UUID) and designate it as the PK. This is a common convention.
*   **Relationship Inference:**
    *   Based on naming conventions: If a column `author_id` in a `posts` table is found, and a `users` table (potentially an alias for "authors") has an `id` column, infer a foreign key relationship. This requires careful handling to avoid incorrect inferences.
    *   Suggest relationships based on NLP output where cardinality was identified.
*   **Normalization Suggestions (Future Enhancement):**
    *   Analyze for repeating groups or potential violations of normal forms (e.g., 2NF, 3NF).
    *   Suggest splitting tables or modifying structures to improve normalization. This is a more advanced feature.
*   **Constraint Suggestion:**
    *   Suggest `NOT NULL` constraints for fields that appear to be mandatory based on context or data sampling.
    *   Suggest `UNIQUE` constraints for fields like `username` or `email`.

## 6. Database-Specific Adapters

*   **Purpose:** To translate the generic Intermediate Schema Representation into the concrete syntax and features of a specific target database system.
*   **Structure:** A set of distinct modules or classes, one for each supported database (e.g., `PostgreSQLAdapter`, `MySQLAdapter`, `SQLiteAdapter`, `MongoDBAdapter`).
*   **Functionality:**
    *   **Type Mapping:** Convert generic data types (STRING, INTEGER, DATETIME) to their database-specific equivalents (e.g., `STRING` -> `VARCHAR(255)` or `TEXT` in PostgreSQL/MySQL; `INTEGER` -> `INT` or `BIGINT`). This mapping may include parameters like length, precision, and scale.
    *   **DDL Generation (for SQL databases):**
        *   Construct `CREATE TABLE` statements, including column definitions, data types, `NULL`/`NOT NULL`, `DEFAULT` values, `PRIMARY KEY`, `UNIQUE`, `CHECK` constraints.
        *   Generate `ALTER TABLE ... ADD CONSTRAINT ... FOREIGN KEY ...` statements (often generated after all `CREATE TABLE` statements to avoid order-of-creation issues).
        *   Generate `CREATE INDEX` statements.
    *   **Schema Definition (for NoSQL databases like MongoDB):**
        *   Generate a JSON Schema document that can be used with MongoDB's schema validation features.
        *   Suggest document structures and embedding strategies based on relationships in the intermediate schema.
    *   **Dialect-Specific Syntax:** Handle variations in SQL syntax for constraints, data types, auto-increment mechanisms (e.g., `AUTO_INCREMENT` in MySQL vs. `SERIAL` or `IDENTITY` in PostgreSQL), character sets, collations, storage engines (for MySQL), etc.
    *   **Output:** A string containing the DDL script or a JSON/BSON structure for NoSQL schema definition.

This detailed breakdown provides a blueprint for developing the Parsing and Analysis Engine, emphasizing its critical role and complex internal workings.
