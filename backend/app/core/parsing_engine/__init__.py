# backend/app/core/parsing_engine/__init__.py

"""
This is the main package for the Parsing and Analysis Engine.

It orchestrates the parsing of various inputs and the generation
of database schemas.
"""

from typing import Optional # Added Optional for source_name
from .intermediate_schema import SchemaISR, TableISR, ColumnISR, ConstraintDetail # Ensure ConstraintDetail is available if needed by any parser
from .parsers.json_parser import parse_json_input
from .parsers.sql_parser import parse_sql_ddl_input
from .parsers.csv_parser import parse_csv_input  # Import CSV parser
from .adapters.mysql_adapter import convert_isr_to_mysql_ddl
# Placeholder for future PostgreSQL adapter import
# from .adapters.postgres_adapter import convert_isr_to_postgres_ddl

class ParsingEngine:
    def __init__(self):
        """
        Initializes the ParsingEngine.
        Parsers and adapters could be registered here, possibly dynamically,
        for greater extensibility.
        """
        self.parsers = {
            "json": parse_json_input,
            "sql": parse_sql_ddl_input,
            "csv": parse_csv_input,
            # Add other parsers like "text" (NLP) when implemented
        }
        self.adapters = {
            "mysql": convert_isr_to_mysql_ddl,
            # Add other adapters like "postgresql" when implemented
        }
        # No specific initialization needed for this basic setup.
        pass

    def generate_schema_from_input(self, input_data: str, input_type: str, source_name: Optional[str] = None) -> SchemaISR:
        """
        Processes the input data and generates an Intermediate Schema Representation (ISR).

        Args:
            input_data: The raw input string (e.g., JSON, SQL DDL, CSV data).
            input_type: A string indicating the type of input (e.g., "json", "sql", "csv").
            source_name: Optional name of the source (e.g., filename), primarily used by CSV parser for table naming.

        Returns:
            An instance of SchemaISR representing the generated schema.

        Raises:
            NotImplementedError: If no parser is available for the specified input_type.
            ValueError: If the input data is invalid for the specified parser.
        """
        print(f"ParsingEngine: Received call to generate_schema_from_input for type '{input_type}', source: '{source_name}'")
        input_type_lower = input_type.lower()

        parser_func = self.parsers.get(input_type_lower)

        if parser_func:
            try:
                if input_type_lower == "csv":
                    # CSV parser has an additional argument for table name based on source
                    return parser_func(input_data, table_name_from_file=source_name)
                else:
                    return parser_func(input_data)
            except ValueError as ve:
                print(f"ValueError during {input_type_lower} parsing: {ve}")
                raise
            except Exception as e:
                print(f"Unexpected error during {input_type_lower} parsing: {e}")
                raise ValueError(f"Error processing {input_type_lower} input: {e}")
        else:
            raise NotImplementedError(f"Parser for input type '{input_type}' is not implemented.")

    def convert_isr_to_target_ddl(self, isr: SchemaISR, target_db: str) -> str:
        """
        Converts an Intermediate Schema Representation (ISR) to a target database DDL string.
        """
        print(f"ParsingEngine: Received call to convert_isr_to_target_ddl for '{target_db}'")
        target_db_lower = target_db.lower()

        adapter_func = self.adapters.get(target_db_lower)

        if adapter_func:
            try:
                return adapter_func(isr)
            except Exception as e:
                print(f"Unexpected error during DDL conversion for {target_db_lower}: {e}")
                raise ValueError(f"Error converting ISR to DDL for {target_db_lower}: {e}")
        else:
            raise NotImplementedError(f"Adapter for target database '{target_db}' is not implemented.")

# Example Usage (for direct testing of this module)
if __name__ == '__main__':
    engine = ParsingEngine()

    # Test CSV parsing
    sample_csv_input = "header1,header2\nval1,val2\n123,45.6"
    try:
        print("\\n--- Testing CSV input to MySQL DDL ---")
        intermediate_schema_csv = engine.generate_schema_from_input(sample_csv_input, "csv", source_name="my_data.csv")
        print(f"Parsed CSV: Found {len(intermediate_schema_csv.tables)} table(s).")
        if intermediate_schema_csv.tables:
            table = intermediate_schema_csv.tables[0]
            print(f"  Table Name (from CSV source_name): {table.name}")
            for col in table.columns:
                print(f"    Column: {col.name} ({col.generic_type})")

        mysql_ddl_from_csv = engine.convert_isr_to_target_ddl(intermediate_schema_csv, "mysql")
        print("MySQL DDL from CSV input:\n", mysql_ddl_from_csv)

    except Exception as e:
        print(f"Error in CSV processing: {e}")

    # ... (other example tests for JSON and SQL can be kept or added here)
    print("\\n--- Example usage finished ---")
