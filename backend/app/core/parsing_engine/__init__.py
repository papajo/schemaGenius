# backend/app/core/parsing_engine/__init__.py

"""
This is the main package for the Parsing and Analysis Engine.

It orchestrates the parsing of various inputs and the generation
of database schemas.
"""

from typing import Optional
from .intermediate_schema import SchemaISR # Keep this minimal for the __init__
from .parsers.json_parser import parse_json_input
from .parsers.sql_parser import parse_sql_ddl_input
from .parsers.csv_parser import parse_csv_input
from .adapters.mysql_adapter import convert_isr_to_mysql_ddl
from .adapters.postgresql_adapter import convert_isr_to_postgresql_ddl # Import PostgreSQL adapter

class ParsingEngine:
    def __init__(self):
        """
        Initializes the ParsingEngine.
        Parsers and adapters are mapped here for dispatch.
        """
        self.parsers = {
            "json": parse_json_input,
            "sql": parse_sql_ddl_input,
            "csv": parse_csv_input,
            # "text": parse_nlp_input, # Future
        }
        self.adapters = {
            "mysql": convert_isr_to_mysql_ddl,
            "postgresql": convert_isr_to_postgresql_ddl,
            "postgres": convert_isr_to_postgresql_ddl, # Alias for postgresql
            # "mssql": convert_isr_to_mssql_ddl, # Future
        }

    def generate_schema_from_input(self, input_data: str, input_type: str, source_name: Optional[str] = None) -> SchemaISR:
        """
        Processes the input data using the appropriate parser and generates an
        Intermediate Schema Representation (ISR).
        """
        print(f"ParsingEngine: Generating schema from '{input_type}' input. Source: '{source_name if source_name else 'N/A'}'")
        input_type_lower = input_type.lower()

        parser_func = self.parsers.get(input_type_lower)
        if not parser_func:
            raise NotImplementedError(f"Parser for input type '{input_type}' is not implemented.")

        try:
            if input_type_lower == "csv":
                return parser_func(input_data, table_name_from_file=source_name)
            else:
                return parser_func(input_data)
        except ValueError as ve:
            print(f"ValueError during '{input_type_lower}' parsing: {ve}")
            raise # Re-raise for API layer to handle as HTTP 400
        except Exception as e:
            # Log the full error traceback in a real application
            print(f"Unexpected error during '{input_type_lower}' parsing: {type(e).__name__} - {e}")
            raise ValueError(f"Error processing '{input_type_lower}' input: {e}") # Re-raise as ValueError

    def convert_isr_to_target_ddl(self, isr: SchemaISR, target_db: str) -> str:
        """
        Converts an Intermediate Schema Representation (ISR) to a target database DDL string
        using the appropriate adapter.
        """
        print(f"ParsingEngine: Converting ISR to '{target_db}' DDL.")
        target_db_lower = target_db.lower()

        adapter_func = self.adapters.get(target_db_lower)
        if not adapter_func:
            raise NotImplementedError(f"Adapter for target database '{target_db}' is not implemented.")

        try:
            return adapter_func(isr)
        except Exception as e:
            # Log the full error traceback in a real application
            print(f"Unexpected error during DDL conversion for '{target_db_lower}': {type(e).__name__} - {e}")
            raise ValueError(f"Error converting ISR to DDL for '{target_db_lower}': {e}") # Re-raise as ValueError

# Example Usage (for direct testing of this module)
if __name__ == '__main__':
    engine = ParsingEngine()

    # Test PostgreSQL DDL Conversion from JSON
    sample_json_input = """
    {
        "schema_name": "LibraryDB_PG", "version": "vPG1",
        "tables": [
            {
                "name": "items",
                "columns": [
                    {"name": "item_id", "generic_type": "INTEGER", "constraints": [{"type": "PRIMARY_KEY"}, {"type":"AUTO_INCREMENT"}]},
                    {"name": "item_name", "generic_type": "TEXT", "constraints": [{"type": "NOT_NULL"}]},
                    {"name": "type", "generic_type": "ENUM_TYPE",
                     "constraints": [{"type":"ENUM_VALUES", "details": {"values": ["book", "cd", "magazine"]}}]}
                ]
            }
        ]
    }
    """
    try:
        print("\\n--- Testing JSON input to PostgreSQL DDL ---")
        intermediate_schema_json_pg = engine.generate_schema_from_input(sample_json_input, "json")
        print(f"Parsed JSON for PG: Schema '{intermediate_schema_json_pg.schema_name}', Version '{intermediate_schema_json_pg.version}'")

        pg_ddl_from_json = engine.convert_isr_to_target_ddl(intermediate_schema_json_pg, "postgresql")
        print("PostgreSQL DDL from JSON input:\n", pg_ddl_from_json)

    except Exception as e:
        print(f"Error in JSON to PostgreSQL processing: {e}")

    # Test SQL input to PostgreSQL DDL
    sample_sql_input_pg = """
    CREATE TABLE "Employees" (
        "EmpID" SERIAL PRIMARY KEY,
        "FullName" VARCHAR(255) NOT NULL,
        "Department" TEXT DEFAULT 'General'
    );
    """
    try:
        print("\\n--- Testing SQL input to PostgreSQL DDL ---")
        intermediate_schema_sql_pg = engine.generate_schema_from_input(sample_sql_input_pg, "sql")
        print(f"Parsed SQL for PG: Found {len(intermediate_schema_sql_pg.tables)} table(s).")
        if intermediate_schema_sql_pg.tables:
            print(f"  Table Name: {intermediate_schema_sql_pg.tables[0].name}")

        pg_ddl_from_sql = engine.convert_isr_to_target_ddl(intermediate_schema_sql_pg, "postgres") # Using alias
        print("PostgreSQL DDL from SQL input:\n", pg_ddl_from_sql)
    except Exception as e:
        print(f"Error in SQL to PostgreSQL processing: {e}")

    print("\\n--- Example usage finished ---")
