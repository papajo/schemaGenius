# Application User Documentation Structure

## 1. Introduction to Documentation

### Purpose
The primary purpose of this documentation is to empower users to effectively understand, utilize, and troubleshoot the SchemaGenius application. It aims to guide users through all features, from initial project creation to final schema export, enabling them to generate accurate and efficient database schemas.

### Target Audience
The documentation is intended for a diverse audience, including:
*   **Beginners in Database Design:** Individuals new to database concepts who need clear, step-by-step guidance.
*   **Software Developers:** Developers who want to quickly generate schemas from existing code or textual descriptions.
*   **Data Analysts/Scientists:** Users who might need to infer schemas from data files.
*   **Experienced Database Administrators (DBAs):** While potentially using more advanced tools, DBAs might use SchemaGenius for quick prototyping or initial drafts.
The language will aim to be clear and accessible, with technical terms explained.

### Accessibility
*   The documentation will be easily accessible, ideally via a "Help" or "Documentation" link within the SchemaGenius application.
*   Consideration will be given to making it available as a standalone, searchable web portal (e.g., `docs.schemageniusapp.com`).

## 2. Main Documentation Sections

### A. Getting Started

*   **1. Welcome / Introduction to SchemaGenius:**
    *   What is SchemaGenius? (Brief overview of its purpose and core functionality)
    *   Key Features and Benefits (e.g., multi-input support, visual editor, export options)
    *   Who is SchemaGenius for? (Relating to the target audience)
*   **2. Account Management (If applicable):**
    *   Creating a SchemaGenius Account
    *   Logging In and Logging Out
    *   Managing Your Profile (e.g., changing password, email preferences)
    *   Subscription/Plan Details (if tiered access)
*   **3. Creating Your First Schema Project:**
    *   Understanding Projects in SchemaGenius (What a project holds)
    *   Step-by-Step Guide: From dashboard to the input page for a new project.
    *   Choosing a good Project Name.
*   **4. Quick Tour of the Interface:**
    *   The Dashboard: Main navigation points, accessing recent projects.
    *   The Project Input Page: Where you provide your source material.
    *   The Schema Editor: A brief visual introduction to the canvas, toolbars, and panels.

### B. Input Methods (Detailed Guides)

This section will have a sub-page for each major input method.

*   **1. Using Code Snippets:**
    *   Overview of supported programming languages and ORMs (SQL, Python - SQLAlchemy/Django, Java - JPA/Hibernate).
    *   **SQL Input:**
        *   Supported DDL statements (focus on `CREATE TABLE`, `ALTER TABLE` for constraints/indexes).
        *   Dialect Considerations: Specific examples and notes for MySQL, PostgreSQL.
        *   Best Practices for SQL Input (e.g., clarity, completeness).
        *   Common Issues: Syntax errors, unsupported features, how to check.
    *   **Python (SQLAlchemy / Django ORM) Input:**
        *   Required class structures, necessary imports, and decorators.
        *   Examples of model definitions for both SQLAlchemy and Django.
        *   How relationships (ForeignKey, OneToMany, ManyToMany) are parsed and inferred.
        *   Supported data types and how they map.
    *   **Java (JPA / Hibernate) Input:**
        *   Essential annotations: `@Entity`, `@Table`, `@Column`, `@Id`, `@GeneratedValue`, relationship annotations (`@OneToOne`, `@ManyToOne`, `@OneToMany`, `@ManyToMany`).
        *   Example entity class definitions.
        *   Parsing custom type converters or embedded objects (if supported).
*   **2. Using Natural Language Descriptions:**
    *   How SchemaGenius Interprets Your Text (a simplified, non-technical explanation of the NLP process).
    *   Tips for Writing Effective Descriptions:
        *   Be explicit about table names (e.g., "Create a table named 'Customers'").
        *   Clearly list field names for each table.
        *   Use precise language for relationships (e.g., "Each Customer can have many Orders," "An Order belongs to one Customer").
        *   Specify data types if known (e.g., "an 'email' field which is text," "a 'quantity' field which is a number").
    *   Examples:
        *   Good examples demonstrating clarity and specificity.
        *   "Before and After": Examples of vague descriptions and how to improve them.
    *   Understanding Confidence Scores and Feedback from the NLP engine.
*   **3. Uploading Data Files (CSV, JSON):**
    *   General: Supported file formats, encoding (e.g., UTF-8 recommended).
    *   **CSV Files:**
        *   Importance of a Header Row for column names.
        *   How Data Types are Inferred (sampling, common patterns).
        *   Handling Delimiters and Quotes.
        *   Uploading Multiple CSV Files (e.g., each file representing a table, and how to indicate relationships if possible).
    *   **JSON Files:**
        *   Expected Structures:
            *   Array of objects (each object a row, keys are columns).
            *   Single object (keys are table names, values describe structure - less common for data-driven input).
        *   Data Type Inference from JSON values.
    *   Limitations: File size recommendations, impact of data sampling on accuracy.

### C. The Schema Editor

*   **1. Understanding the Visual Interface:**
    *   The Canvas: Visual representation of tables/collections, fields, and relationship lines.
    *   Main Toolbar: Key actions like "Add Table," "Save," "Export," "Validate."
    *   Properties/Edit Panel: Contextual panel for editing selected elements (table, field, relationship).
    *   Schema Elements Tree/List: Alternative textual navigation for schema components.
*   **2. Working with Tables/Collections:**
    *   Adding a New Table/Collection.
    *   Renaming Tables.
    *   Deleting Tables (and impact on relationships).
    *   Adding Descriptions/Comments to Tables.
*   **3. Working with Fields/Columns:**
    *   Adding a New Field to an Existing Table.
    *   Editing Field Names.
    *   Understanding and Selecting Data Types (explanation of generic types offered by SchemaGenius and how they map to common DB types).
    *   Defining Constraints:
        *   Primary Key (PK).
        *   Foreign Key (FK) - also covered in Relationships.
        *   Unique (UQ).
        *   Not Null (NN).
    *   Setting Default Values for Fields.
    *   Adding Comments/Descriptions to Fields.
*   **4. Defining Relationships:**
    *   Conceptual Overview: One-to-One, One-to-Many, Many-to-Many.
    *   Creating Relationships using the Visual Editor (e.g., dragging from one field to another).
    *   Editing Relationships via the Properties Panel.
    *   Understanding Foreign Keys: How they are automatically created or manually assigned.
    *   Setting Referential Actions (ON DELETE, ON UPDATE - for SQL targets).
*   **5. Managing Indexes:**
    *   What are Indexes? Why are they important for performance?
    *   Creating Single-Column Indexes.
    *   Creating Composite (Multi-Column) Indexes.
    *   Specifying Index Uniqueness.

### D. Validation and Error Handling

*   **1. Understanding Validation Feedback:**
    *   Real-time Validation: During input and in the schema editor.
    *   Locating Validation Messages: Inline, in a dedicated "Issues" panel, or during export.
    *   Severity Levels: Differentiating between Errors (must fix), Warnings (best practice), and Suggestions/Info.
*   **2. Common Validation Issues and How to Fix Them:**
    *   **Input Errors:** SQL syntax errors, unparsable code, malformed CSV/JSON.
    *   **Structural Errors:** Missing primary keys, orphaned foreign keys, inconsistent relationship types.
    *   **Naming Issues:** Reserved keywords, invalid characters, inconsistent casing.
    *   **Data Type Issues:** Incompatible types for relationships, inappropriate type choices.
    *   For each common issue: Explanation, example, and step-by-step guidance on resolution.

### E. Exporting Your Schema

*   **1. Choosing an Export Format:**
    *   **SQL DDL:** Purpose (direct database deployment), target databases (MySQL, PostgreSQL).
    *   **JSON Schema:** Purpose (integration, documentation, NoSQL validation), structure overview.
    *   **XML Schema:** Purpose (specific integrations), structure overview.
*   **2. Selecting Export Options:**
    *   Target Database (for SQL DDL): How it affects dialect and type mapping.
    *   "Include `DROP TABLE IF EXISTS` statements" (SQL): Purpose and implications.
    *   "Include Comments": How user-added descriptions are carried into the export.
*   **3. Downloading and Using Your Exported Files:**
    *   File naming conventions.
    *   Brief tips on how to use the SQL DDL in common database tools (e.g., phpMyAdmin, pgAdmin, command line).

### F. Best Practices in Database Design (Briefly)

*   Introduction: How SchemaGenius encourages good design but understanding principles helps.
*   Normalization: Basic concept (e.g., avoiding redundant data, 1NF, 2NF, 3NF in simple terms).
*   Choosing Appropriate Data Types: Impact on storage and performance.
*   Consistent Naming Conventions: Importance for readability and maintainability.
*   The Role of Primary and Foreign Keys in data integrity.
*   (This section should be concise and link to external resources for deeper learning).

### G. Troubleshooting / FAQ

*   **Common Problems & Solutions:**
    *   "Schema generation is taking too long." (Possible causes: very large input, complex NLP query).
    *   "The generated schema doesn't look like what I expected from my input." (Tips: review input clarity, NLP ambiguity).
    *   "I'm getting errors when I try to export." (Check validation panel, target DB compatibility).
    *   "My file upload is failing." (Check file format, size limits).
    *   "I can't connect two tables in the editor." (Check for existing PKs, data types).
*   **Frequently Asked Questions:**
    *   What are the specific SQL DDL features supported for MySQL/PostgreSQL?
    *   How does SchemaGenius handle very complex codebases or SQL scripts?
    *   Can I import an existing database schema directly? (If planned: Yes/No/Roadmap).
    *   What are the practical limits on input size or schema complexity?
    *   How is my data privacy handled?

### H. Glossary of Terms

*   Alphabetical list of common database terms (e.g., Table, Column, Primary Key, Foreign Key, Index, DDL, SQL, Normalization, Cardinality) and SchemaGenius-specific terms, with clear definitions.

### I. Contact Support / Feedback

*   How to Get Help: Link to a support channel (e.g., email, forum, ticketing system) if the documentation doesn't solve the problem.
*   Provide Feedback: A link or instructions on how users can provide feedback on the SchemaGenius application or the documentation itself.

## 3. Documentation Format and Delivery

*   **Platform:** A web-based knowledge base system is preferred for ease of access, searchability, and maintenance.
    *   Options: GitBook, ReadtheDocs (if docs are in reStructuredText/Markdown in a repo), Docusaurus, VuePress, or a built-in solution.
*   **Searchability:** A prominent and effective search bar is crucial.
*   **Contextual Help:** Implement links from specific UI elements or features within the SchemaGenius application directly to the relevant documentation page or section.
*   **Versioning:** If the application undergoes significant functional changes, the documentation should be versioned to match the application version.
*   **Visuals:** Use screenshots, GIFs, or short video clips where appropriate to illustrate UI interactions and concepts.
*   **Clear Navigation:** Logical structure with a clear table of contents / sidebar.
*   **Print-Friendly CSS:** (Optional) For users who prefer to print sections.
