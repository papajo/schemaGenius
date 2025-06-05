# backend/app/core/parsing_engine/__init__.py

"""
This is the main package for the Parsing and Analysis Engine.

It orchestrates the parsing of various inputs and the generation
of database schemas.
"""

from .intermediate_schema import SchemaISR, TableISR, ColumnISR, ConstraintDetail
from .parsers.json_parser import parse_json_input
from .parsers.sql_parser import parse_sql_ddl_input  # Import SQL parser
from .adapters.mysql_adapter import convert_isr_to_mysql_ddl
# Placeholder for future PostgreSQL adapter import
# from .adapters.postgres_adapter import convert_isr_to_postgres_ddl

class ParsingEngine:
    def __init__(self):
        """
        Initializes the ParsingEngine.
        Parsers and adapters could be registered here, possibly dynamically.
        """
        self.parsers = {
            "json": parse_json_input,
            "sql": parse_sql_ddl_input,
            # Add other parsers like "text" (NLP) when implemented
        }
        self.adapters = {
            "mysql": convert_isr_to_mysql_ddl,
            # Add other adapters like "postgresql" when implemented
        }
        pass

    def generate_schema_from_input(self, input_data: str, input_type: str) -> SchemaISR:
        """
        Processes the input data and generates an Intermediate Schema Representation (ISR).
        """
        print(f"ParsingEngine: Received call to generate_schema_from_input for type '{input_type}'")
        input_type_lower = input_type.lower()

        parser_func = self.parsers.get(input_type_lower)

        if parser_func:
            try:
                return parser_func(input_data)
            except ValueError as ve: # Specific error from parsers (e.g., JSON format)
                print(f"ValueError during {input_type_lower} parsing: {ve}")
                raise # Re-raise to be handled by API layer
            except Exception as e: # Catch broader exceptions from parsing for now
                # In production, log this exception with traceback
                print(f"Unexpected error during {input_type_lower} parsing: {e}")
                # Re-raise as a ValueError for API consistency, or a custom ParsingError
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
                # In production, log this exception with traceback
                print(f"Unexpected error during DDL conversion for {target_db_lower}: {e}")
                # Re-raise as a ValueError or a custom ConversionError
                raise ValueError(f"Error converting ISR to DDL for {target_db_lower}: {e}")
        else:
            raise NotImplementedError(f"Adapter for target database '{target_db}' is not implemented.")

# Example Usage (for direct testing of this module)
if __name__ == '__main__':
    engine = ParsingEngine()

    # Test JSON parsing and MySQL DDL Conversion
    sample_json_input = """
    {
        "schema_name": "LibraryDB_JSON", "version": "vJ1",
        "tables": [{"name": "Books", "columns": [{"name": "id", "generic_type": "INTEGER", "constraints": [{"type": "PRIMARY_KEY"}]}]}]
    }
    """
    try:
        print("\\n--- Testing JSON input to MySQL DDL ---")
        intermediate_schema_json = engine.generate_schema_from_input(sample_json_input, "json")
        print(f"Parsed JSON: {intermediate_schema_json.schema_name}")
        mysql_ddl_from_json = engine.convert_isr_to_target_ddl(intermediate_schema_json, "mysql")
        print("MySQL DDL from JSON input:\n", mysql_ddl_from_json)
    except Exception as e:
        print(f"Error in JSON processing: {e}")

    # Test SQL parsing and MySQL DDL Conversion
    sample_sql_input = """
    CREATE TABLE Authors (
        author_id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL
    );
    CREATE TABLE Articles (
        article_id INT PRIMARY KEY,
        title TEXT NOT NULL,
        author_id INT, -- Assume FK will be handled by adapter or later step
        CONSTRAINT fk_article_author FOREIGN KEY (author_id) REFERENCES Authors(author_id)
    );
    """
    try:
        print("\\n--- Testing SQL input to MySQL DDL ---")
        intermediate_schema_sql = engine.generate_schema_from_input(sample_sql_input, "sql")
        print(f"Parsed SQL: Found {len(intermediate_schema_sql.tables)} tables.")
        if intermediate_schema_sql.tables:
             for table in intermediate_schema_sql.tables:
                print(f"  Table: {table.name}")
                for col in table.columns:
                    print(f"    Column: {col.name} ({col.generic_type}) Constraints: {[c.type for c in col.constraints]}")

        mysql_ddl_from_sql = engine.convert_isr_to_target_ddl(intermediate_schema_sql, "mysql")
        print("MySQL DDL from SQL input:\n", mysql_ddl_from_sql)
    except Exception as e:
        print(f"Error in SQL processing: {e}")

    print("\\n--- Example usage finished ---")
