# backend/app/core/parsing_engine/adapters/postgresql_adapter.py

from typing import List, Dict, Any, Optional, Set

from ..intermediate_schema import SchemaISR, TableISR, ColumnISR, ConstraintDetail

def _map_generic_type_to_postgresql(col_isr: ColumnISR, custom_enum_types: Set[str]) -> str:
    """Maps generic ISR types to PostgreSQL specific types, using custom enum types if available."""
    generic_type_upper = col_isr.generic_type.upper()

    is_pk = any(c.type.upper() == "PRIMARY_KEY" for c in col_isr.constraints if c.type)
    is_auto_increment = any(c.type.upper() == "AUTO_INCREMENT" for c in col_isr.constraints if c.type)

    if is_pk and is_auto_increment:
        if generic_type_upper == "BIG_INTEGER": return "BIGSERIAL"
        if generic_type_upper == "INTEGER": return "SERIAL"

    if generic_type_upper == "ENUM_TYPE":
        # Convention for type name: "enum_<table>_<column>"
        # This assumes the CREATE TYPE statement for this enum will be generated.
        # The actual table name needs to be passed or inferred for this to be robust.
        # For this version, we'll assume the type name has been pre-generated and is known.
        # A more robust solution might involve passing table_name to this function.
        # Or, the calling function `convert_isr_to_postgresql_ddl` can substitute this.
        # Let's use a convention that the calling function will create this type name.
        # Example: if table is 'users' and column is 'status', type is 'enum_users_status'.
        # We will rely on the main function to map this. For now, return a placeholder or the specific name.
        # This function is called per column, so table context is needed for precise enum type name.
        # For the purpose of this function, we'll return the specific type name if it's in custom_enum_types.
        # This requires the caller to manage the custom_enum_types set and pass the table_name for name generation.
        # This is a simplification.
        # Let's assume the table_name_col_name_enum format is passed if this column IS an enum.
        # This is a slight hack for this function's scope.
        # A better way: call this with table_name and col_name.
        # For now, the main converter will handle the actual enum type name.
        return f"TEXT /* ENUM: {col_isr.name} - Will be replaced by custom type */"


    mapping = {
        "STRING": "VARCHAR(255)", "TEXT": "TEXT", "INTEGER": "INTEGER", "BIG_INTEGER": "BIGINT",
        "FLOAT": "REAL", "DOUBLE_PRECISION": "DOUBLE PRECISION", "DECIMAL": "DECIMAL(10, 2)",
        "BOOLEAN": "BOOLEAN", "DATE": "DATE", "TIME": "TIME WITHOUT TIME ZONE",
        "DATETIME": "TIMESTAMP WITHOUT TIME ZONE", "TIMESTAMP": "TIMESTAMP WITH TIME ZONE",
        "BLOB": "BYTEA", "JSON_TYPE": "JSONB", "UUID_TYPE": "UUID"
    }
    return mapping.get(generic_type_upper, "TEXT") # Default to TEXT for unknown

def _get_column_constraints_ddl(col_isr: ColumnISR, pg_type: str) -> str:
    """Helper to generate constraint strings for a column, aware of SERIAL implications."""
    parts = []
    is_serial_type = "SERIAL" in pg_type.upper() #SERIAL or BIGSERIAL

    has_pk_constraint = False
    for constraint in col_isr.constraints:
        ctype = constraint.type.upper() if constraint.type else ""
        if ctype == "PRIMARY_KEY":
            has_pk_constraint = True # Mark that PK is defined for this col
            if not is_serial_type: # SERIAL implies PK, so don't add it again
                parts.append("PRIMARY KEY")
        elif ctype == "NOT_NULL":
            if not is_serial_type: # SERIAL implies NOT NULL
                 parts.append("NOT NULL")
        elif ctype == "UNIQUE":
            # If it's a PK (especially serial), it's already unique.
            # If it's PK but not serial, PK constraint handles uniqueness.
            # So, add UNIQUE only if it's not a PK.
            is_pk = any(c.type.upper() == "PRIMARY_KEY" for c in col_isr.constraints if c.type)
            if not is_pk:
                parts.append("UNIQUE")
        elif ctype == "DEFAULT":
            default_details = constraint.details
            if default_details:
                value = default_details.get("value")
                if isinstance(value, str):
                    if value.upper() == "CURRENT_TIMESTAMP" or value.upper().startswith("NOW()"): # Common SQL functions
                        parts.append(f"DEFAULT {value.upper()}")
                    else: # Escape single quotes for string literals
                        parts.append(f"DEFAULT '{value.replace("'", "''")}'")
                elif isinstance(value, bool):
                    parts.append(f"DEFAULT {str(value).upper()}")
                elif isinstance(value, (int, float)):
                    parts.append(f"DEFAULT {value}")
        # AUTO_INCREMENT is handled by SERIAL/BIGSERIAL types.
        # FOREIGN KEY and CHECK constraints are typically added at table level or via ALTER TABLE.
    return " ".join(parts)

def convert_isr_to_postgresql_ddl(schema_isr: SchemaISR) -> str:
    all_ddl_statements: List[str] = []
    # Store unique CREATE TYPE statements for ENUMs: (type_name, sql_statement)
    enum_type_creations: Dict[str, str] = {}
    foreign_key_alter_statements: List[str] = []
    column_comments: List[str] = []
    table_comments: List[str] = []

    if schema_isr.schema_name: all_ddl_statements.append(f"-- Schema: {schema_isr.schema_name}")
    if schema_isr.version: all_ddl_statements.append(f"-- Version: {schema_isr.version}")
    all_ddl_statements.append("-- Generated by SchemaGenius for PostgreSQL\n")

    # Pass 1: Define ENUM types
    for table_isr in schema_isr.tables:
        for col_isr in table_isr.columns:
            if col_isr.generic_type.upper() == "ENUM_TYPE":
                enum_values_detail = next((c for c in col_isr.constraints if c.type.upper() == "ENUM_VALUES"), None)
                if enum_values_detail and isinstance(enum_values_detail.details.get("values"), list):
                    enum_vals = enum_values_detail.details["values"]
                    if enum_vals:
                        # Sanitize for type name (PostgreSQL identifiers are case-insensitive unless quoted)
                        type_name = f"enum_{_clean_identifier(table_isr.name)}_{_clean_identifier(col_isr.name)}".lower()
                        if type_name not in enum_type_creations:
                            formatted_enum_values = ", ".join([f"'{str(val).replace("'", "''")}'" for val in enum_vals])
                            enum_type_creations[type_name] = f"CREATE TYPE \"{type_name}\" AS ENUM ({formatted_enum_values});"

    if enum_type_creations:
        all_ddl_statements.append("-- Custom ENUM types")
        all_ddl_statements.extend(sorted(list(enum_type_creations.values())))
        all_ddl_statements.append("")

    # Pass 2: Create Tables
    for table_isr in schema_isr.tables:
        column_definitions: List[str] = []
        # For table-level constraints like multi-column PKs or specific named constraints
        table_level_constraints_str: List[str] = []

        # Collect PK column names for potential table-level PK definition
        pk_cols_for_table_constraint: List[str] = []

        for col_isr in table_isr.columns:
            pg_type: str
            if col_isr.generic_type.upper() == "ENUM_TYPE":
                # Use the conventional name. Assumes it was created.
                pg_type = f"\"enum_{_clean_identifier(table_isr.name)}_{_clean_identifier(col_isr.name)}\"".lower()
            else:
                pg_type = _map_generic_type_to_postgresql(col_isr, set(enum_type_creations.keys()))

            is_serial = "SERIAL" in pg_type.upper()
            constraints_str = _get_column_constraints_ddl(col_isr, is_serial)

            col_def_parts = [f"    \"{_clean_identifier(col_isr.name)}\" {pg_type}"]
            if constraints_str:
                col_def_parts.append(constraints_str)
            column_definitions.append(" ".join(col_def_parts))

            if col_isr.comment:
                column_comments.append(f"COMMENT ON COLUMN \"{_clean_identifier(table_isr.name)}\".\"{_clean_identifier(col_isr.name)}\" IS '{col_isr.comment.replace("'", "''")}';")

            # Collect PK cols for table-level constraint if not serial (SERIAL implies PK)
            if any(c.type.upper() == "PRIMARY_KEY" for c in col_isr.constraints if c.type) and not is_serial:
                pk_cols_for_table_constraint.append(f"\"{_clean_identifier(col_isr.name)}\"")

            # Collect FK constraints for ALTER TABLE statements
            for constraint in col_isr.constraints:
                if constraint.type.upper() == "FOREIGN_KEY":
                    details = constraint.details
                    fk_name = details.get("name", f"fk_{_clean_identifier(table_isr.name)}_{_clean_identifier(col_isr.name)}")
                    ref_table = _clean_identifier(details.get("references_table", ""))
                    ref_cols_list = details.get("references_columns", []) # Should be a list
                    if ref_table and ref_cols_list and isinstance(ref_cols_list, list) and ref_cols_list:
                        ref_cols_str = ", ".join([f"\"{_clean_identifier(rc)}\"" for rc in ref_cols_list])
                        on_delete = details.get("on_delete", "NO ACTION").upper()
                        on_update = details.get("on_update", "NO ACTION").upper()
                        fk_actions = ""
                        if on_delete and on_delete != "NO ACTION": fk_actions += f" ON DELETE {on_delete}"
                        if on_update and on_update != "NO ACTION": fk_actions += f" ON UPDATE {on_update}"

                        # Add as ALTER TABLE for clarity and to avoid order issues.
                        # Could also be added as table-level constraint if preferred and no order issues.
                        foreign_key_alter_statements.append(
                            f"ALTER TABLE \"{_clean_identifier(table_isr.name)}\" ADD CONSTRAINT \"{_clean_identifier(fk_name)}\" "
                            f"FOREIGN KEY (\"{(col_isr.name)}\") REFERENCES \"{ref_table}\" ({ref_cols_str}){fk_actions};"
                        )

        # Add table-level primary key if multiple columns are part of it, or if it's a single non-SERIAL PK
        if pk_cols_for_table_constraint:
             table_level_constraints_str.append(f"    PRIMARY KEY ({', '.join(pk_cols_for_table_constraint)})")

        # Assemble CREATE TABLE
        if not column_definitions: continue

        all_col_and_table_constraints = column_definitions + table_level_constraints_str
        create_table_statement = (f"CREATE TABLE \"{_clean_identifier(table_isr.name)}\" (\n" +
                                  ",\n".join(all_col_and_table_constraints) +
                                  "\n);")
        all_ddl_statements.append(create_table_statement)

        if table_isr.comment:
            table_comments.append(f"COMMENT ON TABLE \"{_clean_identifier(table_isr.name)}\" IS '{table_isr.comment.replace("'", "''")}';")
        all_ddl_statements.append("") # Blank line after each table

    # Append FKs and comments at the end
    if foreign_key_alter_statements:
        all_ddl_statements.append("-- Foreign Key Constraints (added via ALTER TABLE)")
        all_ddl_statements.extend(foreign_key_alter_statements)
        all_ddl_statements.append("")

    if table_comments:
        all_ddl_statements.append("-- Table Comments")
        all_ddl_statements.extend(table_comments)
        all_ddl_statements.append("")

    if column_comments:
        all_ddl_statements.append("-- Column Comments")
        all_ddl_statements.extend(column_comments)
        all_ddl_statements.append("")

    return "\n".join(all_ddl_statements)

def _clean_identifier(name: Optional[str]) -> str:
    """Cleans an identifier for SQL (e.g. table/column name) by removing quotes."""
    if name is None: return ""
    return name.strip('`"\'')
