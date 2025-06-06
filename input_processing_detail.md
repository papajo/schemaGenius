# Input Processing Detail

This document details the processing strategy for each supported input type, outlining how raw user input is transformed into an intermediate representation suitable for schema generation.

## 1. Code Snippet Processing

This section describes how code snippets from various programming languages are parsed to extract database schema information.

*   **Supported Languages:** Initially SQL (various dialects like MySQL, PostgreSQL), Python (focus on ORM definitions like SQLAlchemy, Django ORM), Java (focus on JPA/Hibernate annotations).
*   **Parsing Strategy:**
    *   **Language Detection:** Use heuristics (keywords, syntax patterns) or a lightweight detection library to identify the language of the provided code snippet.
    *   **SQL:**
        *   Utilize an SQL parsing library (e.g., `sqlparse` for Python, or generate a parser with ANTLR for more complex analysis like dialect-specific features).
        *   Extract: `CREATE TABLE` statements (table names, column names, data types, constraints like `PRIMARY KEY`, `FOREIGN KEY`, `NOT NULL`, `UNIQUE`), `ALTER TABLE` (for modifications), `CREATE INDEX`.
    *   **Python:**
        *   Use Abstract Syntax Tree (AST) parsing (Python's `ast` module).
        *   Identify ORM class definitions (e.g., classes inheriting from `db.Model` in Flask-SQLAlchemy or `models.Model` in Django).
        *   Extract: Class names (as table names), attributes/fields (as column names), data types (e.g., `db.String`, `models.CharField`), relationship definitions (`db.relationship`, `models.ForeignKey`).
    *   **Java:**
        *   Use a Java parser (e.g., JavaParser library or ANTLR with a Java grammar).
        *   Identify entities annotated with `@Entity`.
        *   Extract: Class names (as table names), fields annotated with `@Column` (column names, data types from field types), relationship annotations (`@OneToOne`, `@OneToMany`, `@ManyToOne`, `@ManyToMany`).
*   **Extracted Intermediate Representation:**
    *   Table names
    *   Column names, inferred data types, constraints (PK, FK, nullable, unique)
    *   Relationship details (type, source/target tables and columns)
    *   Source of information (e.g., specific file, line numbers) for traceability.

## 2. Natural Language Description Processing

This section outlines the strategy for interpreting natural language text to infer database schema elements.

*   **Strategy:**
    *   **Preprocessing:** Text cleaning (lowercase, remove punctuation), tokenization, lemmatization/stemming.
    *   **Entity Recognition (NER):** Use NLP libraries (spaCy, NLTK) with custom training or rule-based patterns to identify potential table names (e.g., nouns like "users", "products", "orders") and column names (e.g., "customer name", "order date", "product price").
    *   **Relationship Extraction:**
        *   Analyze sentence structure, verb phrases, and prepositions (e.g., "A customer can have multiple orders," "Each product belongs to a category").
        *   Look for keywords indicating relationships (e.g., "has a", "contains", "belongs to", "references").
        *   Identify cardinality (one-to-one, one-to-many, many-to-many) based on phrasing (e.g., "a user has many posts" vs "a user has one profile").
    *   **Attribute-Entity Association:** Link identified attributes/columns to their respective entities/tables.
*   **Libraries/Tools:**
    *   Python: spaCy (for NER, part-of-speech tagging, dependency parsing), NLTK (for foundational NLP tasks).
    *   Consider fine-tuning pre-trained language models for better domain-specific entity and relationship extraction if a large dataset becomes available.
*   **Interactive Clarification:** If ambiguities arise (e.g., "User details" - what details?), the system should be prepared to flag these for user clarification or make educated guesses with options to override.
*   **Extracted Intermediate Representation:** Similar to code snippets, but with potentially lower confidence scores or flags for ambiguity. Will include identified entities, attributes, and relationships.

## 3. File Upload Processing

This section details how structured files like CSV and JSON are processed.

*   **Supported File Types:** CSV, JSON. (Future: XML, Excel).
*   **CSV Processing:**
    *   **Parsing:** Use standard CSV parsing libraries (e.g., Python's `csv` module, PapaParse in JavaScript).
    *   **Header Row:** Assume the first row contains column headers. If not, allow user to specify or attempt to infer generic names (column_1, column_2).
    *   **Data Type Inference:** Analyze a sample of rows (e.g., first 100-1000 rows) for each column to infer data types (Integer, Float, Boolean, Date, String). Consider consistency and potential for mixed types.
    *   **Relationship Clues:** Look for column names that suggest foreign keys (e.g., `user_id`, `order_id`).
*   **JSON Processing:**
    *   **Parsing:** Use standard JSON parsing libraries (e.g., Python's `json` module, `JSON.parse` in JavaScript).
    *   **Structure Analysis:**
        *   If a list of objects, assume each object represents a row and keys represent columns.
        *   If a single object with nested objects, it might represent multiple related tables or a document structure for NoSQL.
        *   Handle nested structures by either flattening (suggesting related tables) or mapping to complex types/JSON fields if the target DB supports it.
    *   **Data Type Inference:** Similar to CSV, analyze values associated with keys across multiple objects/documents.
*   **Extracted Intermediate Representation:** Table names (possibly derived from filenames or top-level JSON keys), column names, inferred data types, and potential relationships.

## General Considerations for All Input Types

*   **Conflict Resolution:** If multiple inputs are provided (e.g., a SQL snippet and a natural language description), the system will need a strategy to merge or highlight discrepancies in the extracted information. Initially, it might process them separately and then offer a way to combine or choose.
*   **Intermediate Representation:** All parsing processes should output a standardized intermediate data structure (as defined in `application_architecture.md`) that the Schema Generation Logic can consume. This structure should be rich enough to capture all extracted details, including source and confidence levels where applicable.
