# backend/app/core/parsing_engine/parsers/json_parser.py

import json
from typing import Dict, List, Any, Optional

from ..intermediate_schema import SchemaISR, TableISR, ColumnISR, ConstraintDetail

def parse_json_input(json_data: str) -> SchemaISR:
    """
    Parses a JSON string representing a database schema into SchemaISR objects.

    Expected JSON structure:
    {
        "schema_name": "MyDatabase",  # Optional
        "version": "1.0",  # Optional
        "tables": [
            {
                "name": "users",
                "comment": "Stores user information", # Optional
                "columns": [
                    {"name": "id", "generic_type": "INTEGER", "comment": "User ID", "constraints": [{"type": "PRIMARY_KEY"}]},
                    {"name": "email", "generic_type": "STRING", "constraints": [{"type": "UNIQUE"}, {"type": "NOT_NULL"}]}
                ]
            }
        ]
    }
    """
    try:
        data: Dict[str, Any] = json.loads(json_data)
    except json.JSONDecodeError as e:
        # Consider logging the error as well
        raise ValueError(f"Invalid JSON format: {e}")

    schema_name: Optional[str] = data.get("schema_name")
    schema_version: Optional[str] = data.get("version")
    raw_tables: Optional[List[Dict[str, Any]]] = data.get("tables")

    if not isinstance(raw_tables, list):
        raise ValueError("Missing or invalid 'tables' list in JSON input.")

    tables_isr: List[TableISR] = []
    for table_data in raw_tables:
        if not isinstance(table_data, dict):
            # Potentially log this skip or error more gracefully
            raise ValueError(f"Invalid table entry in 'tables' list (expected dict): {table_data}")

        table_name: Optional[str] = table_data.get("name")
        table_comment: Optional[str] = table_data.get("comment")
        raw_columns: Optional[List[Dict[str, Any]]] = table_data.get("columns")

        if not table_name:
            raise ValueError(f"Missing 'name' for table: {table_data}")
        if not isinstance(raw_columns, list):
            raise ValueError(f"Missing or invalid 'columns' list for table '{table_name}'.")

        columns_isr: List[ColumnISR] = []
        for col_data in raw_columns:
            if not isinstance(col_data, dict):
                raise ValueError(f"Invalid column entry in table '{table_name}' (expected dict): {col_data}")

            col_name: Optional[str] = col_data.get("name")
            col_type: Optional[str] = col_data.get("generic_type") # Changed from type to generic_type for consistency
            col_comment: Optional[str] = col_data.get("comment")
            raw_constraints: Optional[List[Dict[str, Any]]] = col_data.get("constraints")

            if not col_name or not col_type:
                raise ValueError(f"Missing 'name' or 'generic_type' for column in table '{table_name}': {col_data}")

            constraints_isr: List[ConstraintDetail] = []
            if isinstance(raw_constraints, list):
                for const_data in raw_constraints:
                    if not isinstance(const_data, dict) or not const_data.get("type"):
                        raise ValueError(f"Invalid constraint format for column '{col_name}' in table '{table_name}': {const_data}")
                    constraints_isr.append(ConstraintDetail(const_data))

            columns_isr.append(ColumnISR(name=col_name, generic_type=col_type, constraints=constraints_isr, comment=col_comment))

        current_table_isr = TableISR(name=table_name, columns=columns_isr, comment=table_comment)
        tables_isr.append(current_table_isr)

    # Create SchemaISR object and assign schema_name and version if they exist
    schema_obj = SchemaISR(tables=tables_isr, schema_name=schema_name, version=schema_version)
    return schema_obj
