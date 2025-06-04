# Validation and Error Handling

This document specifies the validation and error handling mechanisms for the application, aiming to guide users effectively in creating robust database schemas.

## I. Guiding Principles for Validation and Error Handling

*   **Proactive & Real-time (where possible):** Validate inputs and schema changes as early and as continuously as possible, ideally providing feedback in real-time as the user works.
*   **Clear & Actionable Messages:** Error and warning messages must be easy to understand, clearly explain the nature of the problem, and, where possible, suggest concrete solutions or next steps.
*   **Non-Blocking (for warnings):** Distinguish between critical errors that prevent progression (e.g., inability to generate a valid schema) and warnings that suggest best practices or point out potential issues that don't halt the process.
*   **Contextual:** Display error messages and warnings as close as possible to the source of the problem within the UI (e.g., highlighting the specific table, column, or relationship in the visual editor).
*   **Comprehensive:** Implement validation checks across various stages, from initial input parsing to final schema integrity checks against target database system rules.

## II. Validation Stages and Types

### A. Input Parsing Validation

Validation checks performed as the system initially processes user-provided inputs.

*   **Code Snippets (SQL, Python ORM, Java JPA):**
    *   **Syntax Errors:** Basic syntax validation for the specified language (SQL, Python, Java). Report errors directly from the underlying parser (e.g., "SQLSyntaxErrorException: unexpected token 'CREAT' at line 1, column 1").
    *   **Unrecognized Constructs:** If the code uses highly experimental or unsupported ORM features, or very obscure SQL dialect-specific constructs not yet supported, flag these as "Unsupported Feature" or "Partial Support."
*   **Natural Language Descriptions:**
    *   **Ambiguity Detection:** Flag phrases that are too vague or could be interpreted in multiple ways (e.g., Input: "Item details"; Warning: "Phrase 'Item details' is ambiguous. Please specify which details (e.g., 'Item has a name, description, and price')."). Prompt the user for clarification or offer interpretations.
    *   **Low Confidence Extractions:** If the NLP model's confidence for an extracted entity, attribute, or relationship is below a certain threshold, highlight it for user review and confirmation (e.g., "Warning: Low confidence identifying 'status' as an attribute of 'Order'. Please confirm.").
*   **File Uploads (CSV, JSON):**
    *   **Unsupported File Types:** Reject files that are not in the supported formats (e.g., CSV, JSON). Error: "Unsupported file type: '.xlsx'. Please upload a CSV or JSON file."
    *   **Malformed Files:** Report errors if a CSV file is improperly formatted (e.g., inconsistent column counts in rows without quoting) or if a JSON file is syntactically invalid. Error: "Invalid JSON format: Unexpected token ',' at position 54."
    *   **Inconsistent Data (Warnings):** For CSV/JSON, if a column is inferred as Integer but contains many non-numeric values, issue a warning. Warning: "Column 'Age' in 'employees.csv' inferred as Integer, but contains non-numeric values (e.g., 'N/A', 'Unknown'). This may cause data type issues."
    *   **Missing Headers (CSV):** If headers are expected (default or user-specified) but not found in a CSV file, prompt the user. Warning: "CSV file 'data.csv' appears to be missing a header row. Please specify if headers are present or proceed with auto-generated column names."

### B. Intermediate Representation (IR) Validation

Checks performed after initial parsing, on the structured data before full schema generation.

*   **Orphaned Elements:** Check for attributes or relationships that are defined but do not link to any recognized entity (e.g., an attribute `color` was extracted but not associated with any table). Warning: "Extracted attribute 'color' is not associated with any entity. Please assign it or remove it."
*   **Conflicting Information:** If different input sources (e.g., a SQL snippet and an NLP description) define the same entity or attribute with conflicting properties (e.g., different data types for the same column), flag this for user resolution. Warning: "Conflict for 'User.email': SQL defines as VARCHAR(100), NLP suggests it could be TEXT. Please resolve."

### C. Schema Generation & Refinement Validation (Most Critical)

Checks performed during and after the user edits the schema in the visual editor.

*   **Naming Conventions:**
    *   **Invalid Characters:** Check for table and column names containing characters not allowed by SQL standards or the specific target database (e.g., spaces, special symbols unless quoted appropriately). Error: "Invalid character ' ' in table name 'Order Details'. Consider using 'Order_Details'."
    *   **Reserved Keywords:** Warn if names match SQL reserved keywords or keywords specific to the target database. Warning: "Column name 'Order' in table 'Customer' is a reserved keyword in SQL. Consider renaming to 'Order_Name' or similar."
    *   **Uniqueness:** Ensure table names are unique within the schema and column names are unique within their respective tables. Error: "Duplicate table name 'Products'. Table names must be unique."
*   **Primary Keys (PKs):**
    *   **Missing PKs:** Warn if a table lacks a primary key. This can be a configurable setting, as some advanced scenarios might allow this. Warning: "Table 'Audit_Log' does not have a primary key. Consider adding one for optimal performance and data integrity."
    *   **Multiple PKs:** Error if more than one primary key is explicitly defined for a single table (auto-generated composite PKs for join tables are an exception and valid). Error: "Table 'User_Roles' has multiple primary keys defined. A table can have only one primary key."
*   **Foreign Keys (FKs):**
    *   **Referential Integrity:**
        *   Error: "Foreign key 'FK_Order_Customer' in table 'Orders' references non-existent table 'Customers'." (if 'Customers' table was renamed or deleted).
        *   Error: "Foreign key 'FK_Order_Details_Product' references non-existent column 'product_id_typo' in table 'Products'. Did you mean 'product_id'?"
        *   Error: "Data type mismatch for foreign key 'FK_Item_Supplier'. Column 'Items.supplier_id' (INT) does not match referenced column 'Suppliers.supplier_key' (VARCHAR)."
    *   **Circular Dependencies:** Detect direct A->B and B->A FK relationships that might cause issues with data insertion or DDL generation in some RDBMS. Warning: "Circular dependency detected: 'TableA' references 'TableB' and 'TableB' references 'TableA'. This might require deferred constraints or careful data loading strategies."
*   **Data Types:**
    *   **Unsupported Types:** If a data type was specified (e.g., manually entered) that isn't valid for the selected target database system. Error: "Data type 'NUMBERZ' for column 'quantity' in table 'Inventory' is not a valid type for PostgreSQL."
    *   **Incompatible Constraints:** E.g., a `TEXT` or `BLOB` type column marked as `UNIQUE` (possible in some DBs but often very inefficient or with limitations; issue a warning). Warning: "Column 'description' (TEXT) in table 'Documents' is marked UNIQUE. This can lead to performance issues. Consider if this is necessary."
*   **Relationships:**
    *   **Incomplete Relationship Definition:** A relationship is visually drawn or defined but is missing source or target columns. Error: "Incomplete relationship: Please specify source and target columns for the relationship between 'Users' and 'Profiles'."
*   **Database Specific Rules:**
    *   **Length Limits:** Check for table, column, or index names exceeding the maximum length allowed by the target database. Error: "Table name 'a_very_long_table_name_that_exceeds_the_limit' is too long for MySQL (max 64 characters)."
    *   Validate against other specific limitations or features of the selected target (MySQL, PostgreSQL, MongoDB, etc.).

### D. Best Practice Checks (Warnings)

These are suggestions rather than strict errors, aimed at improving schema quality.

*   **Normalization Suggestions (Future Advanced Feature):**
    *   Detecting repeating groups of columns (e.g., `phone1`, `phone2`, `phone3`) that could indicate a need for a separate related table. Warning: "Columns 'phone1, phone2' in 'Contacts' suggest a repeating group. Consider creating a separate 'PhoneNumbers' table."
    *   Identifying potential transitive dependencies.
*   **Overly Large Number of Columns:** Warn if a table has an excessive number of columns (e.g., >50), which might indicate poor design. Warning: "Table 'LegacyData' has 75 columns. Consider if this table could be split for better organization."
*   **Use of Generic Data Types:** Warn when overly generic data types are used where more specific ones might be better (e.g., using `VARCHAR(MAX)` or `TEXT` for fields that are known to be short, like a status flag). Warning: "Column 'status' in 'Tasks' uses VARCHAR(255). If values are short (e.g., 'open', 'closed'), consider a shorter VARCHAR or an ENUM type."
*   **Missing Indexes on Foreign Keys:** Warn if foreign key columns are not indexed, as this can impact join performance. (Note: Many modern RDBMS automatically create indexes on FKs, but it's a good check). Warning: "Column 'user_id' in table 'Posts' is a foreign key but is not indexed. Consider adding an index to improve query performance."

## III. Error Message Presentation

How errors and warnings are communicated to the user.

*   **UI Integration:**
    *   **Visual Schema Editor:** Problematic elements (tables, columns, relationships) are visually highlighted (e.g., with red borders, icons, or different coloring). Hovering over these elements with the mouse cursor reveals a tooltip with the specific error message.
    *   **Properties Panel:** When a table, column, or relationship is selected, any errors or warnings relevant to that specific element are displayed directly within its properties panel.
    *   **Global "Issues" List/Panel:** A dedicated, collapsib_le area in the UI (e.g., a sidebar or bottom panel) that lists all current errors and warnings across the entire schema.
        *   Each item in the list should be clickable, which will navigate the user to and highlight the problematic element in the schema editor.
        *   Error messages should be concise but provide enough detail for understanding.
        *   Consider including unique error codes for easy reference (e.g., "E1023", "W2001"), which can be useful for documentation or support inquiries.
*   **Message Structure (Example):**
    *   **Severity:** [ERROR] / [WARNING]
    *   **Location:** (e.g., "Table 'Users', Column 'email_address'")
    *   **Problem:** (e.g., "Data type mismatch in foreign key relationship.")
    *   **Suggestion:** (e.g., "Ensure 'Orders.user_id' (currently INT) and 'Users.id' (currently STRING) have compatible data types, e.g., both INT.")

## IV. User Correction Flow

1.  User performs an action (e.g., types an input, changes a data type, adds a relationship, modifies a name).
2.  The system validates the input or the change, either in real-time or upon an explicit "validate" action.
3.  If an error or warning is detected:
    *   It is displayed immediately in context (e.g., highlighting the field or schema element) and/or added to the global "Issues" panel.
    *   The problematic part of the schema might be visually marked (e.g., red border).
4.  The user reviews the error message(s) and the provided suggestions.
5.  The user makes corrections based on the feedback (e.g., changes a data type, renames a column, completes a relationship definition).
6.  The system re-validates (often automatically upon change). The error or warning message disappears if the issue is resolved.

## V. Logging

*   **Backend Logging:** The backend application should log significant validation failures, especially those that might indicate bugs or edge cases in the parsing or schema generation logic. These logs should include relevant context.
*   **User-Facing Error Logging (Optional Telemetry):** If telemetry is implemented, user-facing errors (and potentially warnings) can be logged (anonymously, with user consent) to help identify common points of confusion or areas where the application's guidance can be improved.

This comprehensive approach to validation and error handling aims to make the schema design process a helpful and guided experience, rather than a frustrating trial-and-error exercise.
