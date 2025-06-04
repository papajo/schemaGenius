# Schema Generation Logic

This document details the logic for transforming the intermediate representation (IR), derived from user inputs, into a formal database schema suitable for various target database systems.

## 1. Consuming the Intermediate Representation (IR)

*   The Schema Generation Logic takes the structured IR (as defined in `application_architecture.md` and produced by the Input Processing step) as its input.
*   This IR contains lists of potential entities (tables), attributes (columns), their raw data types or values, and detected relationships, often with associated confidence scores or source information.

## 2. Core Schema Refinement and Enrichment

This phase focuses on cleaning, standardizing, and enhancing the raw information from the IR.

*   **Entity Consolidation:**
    *   Merge duplicate or highly similar entities identified from different sources (e.g., "User" table from code and "Customers" from text). This may involve heuristics based on name similarity (e.g., using stemming or Levenshtein distance) or user confirmation in ambiguous cases.
    *   Assign a primary, canonical name to each consolidated entity (which will become a table name).
*   **Attribute Finalization:**
    *   For each entity, consolidate its attributes gathered from various inputs.
    *   Resolve naming conflicts for attributes (e.g., `user_ID` vs `userID` vs `user_identifier`). Standardize attribute names to a consistent convention (e.g., snake_case like `user_id` or camelCase like `userId`). This convention could be user-configurable.
*   **Data Type Determination:**
    *   **Explicit Types:** If data types are explicitly provided (e.g., from SQL `CREATE TABLE` statements or ORM definitions like `String`, `Integer`), these are prioritized. These explicit types are mapped to a canonical internal type system (e.g., "InternalString", "InternalInteger") before later translation to the target database system's specific types.
    *   **Inferred from Data Samples (CSV/JSON):**
        *   Use a predefined hierarchy for type inference (e.g., Boolean -> Integer -> Long -> Float -> Double -> Decimal -> Date -> Timestamp -> String). A column is typed to the most specific type that can accommodate all its sampled values without data loss.
        *   Consider user overrides for these inferred types.
        *   Define rules for string length (e.g., `VARCHAR(255)` as a default, or dynamically determined based on the maximum observed length in samples, possibly with a configurable upper cap).
    *   **Inferred from Natural Language:** Use heuristics based on attribute names or descriptions (e.g., "age" implies an integer, "email_address" implies a string, "is_active" implies boolean). These inferences should be treated with lower confidence and highlighted for user review.
*   **Primary Key (PK) Identification/Generation:**
    *   Prioritize explicitly defined PKs from input sources (e.g., `PRIMARY KEY` constraint in SQL, `@Id` annotation in JPA).
    *   Look for common PK naming patterns (e.g., `id`, `uuid`, `entity_name_id`).
    *   If no PK is clearly identified for an entity, automatically generate one (e.g., an auto-incrementing integer column named `id` or a UUID column). This behavior should be user-configurable (enable/disable, choose type).
*   **Constraint Application:**
    *   Apply `NOT NULL`, `UNIQUE` constraints if they were explicitly defined in the input or can be strongly inferred (e.g., a column named `email` might be a candidate for a `UNIQUE` constraint).
    *   Default values: Allow specification of default values if provided in the input or if a common value appears consistently in data samples (with user confirmation).

## 3. Relationship Processing

This phase establishes formal relationships between entities.

*   **Foreign Key (FK) Creation:**
    *   Translate relationships identified in the IR (e.g., `posts.user_id` references `users.id`) into FK constraints.
    *   Verify that the referenced PKs exist in the target entities.
    *   Define `ON DELETE` / `ON UPDATE` actions (e.g., `CASCADE`, `SET NULL`, `RESTRICT`). These can have configurable defaults (e.g., `RESTRICT` by default) or be inferred from the input if specified (common in some ORM definitions).
*   **Many-to-Many Relationships:**
    *   Identify M:N relationships from the IR. These might be explicitly defined in ORMs or inferred from NLP (e.g., "students enroll in many courses, and courses have many students").
    *   Automatically create junction/join tables for these relationships.
        *   Adopt a clear naming convention for junction tables (e.g., `entity1_entity2` or `entity1_rel_entity2`).
        *   The junction table will include FK columns referencing the primary keys of both related entities. These FKs typically form a composite primary key for the junction table.

## 4. Target Database System Adaptation

The refined, system-agnostic internal schema representation is now translated into the specifics of the user-chosen target database system.

*   **Type Mapping:** Convert the canonical internal data types to the specific syntax and types of the chosen target database:
    *   **MySQL:** `INT`, `BIGINT`, `VARCHAR(n)`, `TEXT`, `DATETIME`, `TIMESTAMP`, `BOOLEAN` (often `TINYINT(1)`), `DECIMAL`, etc.
    *   **PostgreSQL:** `INTEGER`, `BIGINT`, `VARCHAR(n)`, `TEXT`, `TIMESTAMP WITH TIME ZONE`, `BOOLEAN`, `NUMERIC`, `JSONB`, `UUID`, etc.
    *   **MongoDB:** This translates to generating a collection structure.
        *   Fields will map to BSON types (String, NumberInt, NumberLong, Double, Boolean, Date, Array, Object, ObjectId).
        *   Relationships are handled differently:
            *   **Embedding:** For one-to-few relationships where data is closely tied, embed sub-documents.
            *   **Referencing:** For one-to-many or many-to-many, store `ObjectId` references in one document/collection that point to documents in another collection (analogous to FKs).
*   **Syntax Generation:** Generate Data Definition Language (DDL) statements (`CREATE TABLE`, `ALTER TABLE`, `CREATE INDEX`) for SQL databases, or collection creation/validation scripts for MongoDB.
    *   Handle auto-increment/serial keywords (`AUTO_INCREMENT` for MySQL, `SERIAL` or `GENERATED BY DEFAULT AS IDENTITY` for PostgreSQL).
    *   Correctly format constraints (PK, FK, UNIQUE, CHECK, NOT NULL), FK definitions with `ON UPDATE`/`ON DELETE` clauses, and index definitions according to the target system's syntax.
*   **Index Generation:**
    *   Automatically create indexes on all Primary Keys.
    *   By default, create indexes on Foreign Key columns (this is usually beneficial for join performance). This should be a user-configurable option.
    *   Allow users to specify additional columns or combinations of columns to be indexed based on anticipated query patterns.

## 5. Schema Validation (Pre-Export)

Before outputting the final schema, perform a series of validation checks.

*   Check for:
    *   Missing Primary Keys on tables (if not explicitly allowed by configuration).
    *   Foreign Keys referencing non-existent tables or columns.
    *   Data type mismatches between FK columns and the PK columns they reference.
    *   Circular dependencies that might cause issues during DDL execution in some database systems.
    *   Adherence to naming conventions and length limitations of the target database system (e.g., max table name length).
    *   Unsupported features for the target database (e.g., trying to use a feature specific to PostgreSQL when targeting MySQL).
*   Provide clear warnings or errors to the user for any issues found, guiding them to resolve potential problems.

## 6. Output

*   The final, validated schema, ready for export in the user-selected format. This could be:
    *   An SQL DDL script (`.sql`).
    *   A JSON or BSON representation for MongoDB collection structures and validation rules.
    *   Other formats as required (e.g., ORM model code stubs).

This structured approach ensures that the generated schema is robust, consistent, and tailored to the chosen database technology.
