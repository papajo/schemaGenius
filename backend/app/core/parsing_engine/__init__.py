# backend/app/core/parsing_engine/__init__.py

"""
This is the main package for the Parsing and Analysis Engine.

It orchestrates the parsing of various inputs and the generation
of database schemas.
"""

from .intermediate_schema import SchemaISR, TableISR, ColumnISR, ConstraintDetail # Ensure ConstraintDetail is imported
from .parsers.json_parser import parse_json_input
from .adapters.mysql_adapter import convert_isr_to_mysql_ddl # Import MySQL adapter
# Placeholder for future PostgreSQL adapter import
# from .adapters.postgres_adapter import convert_isr_to_postgres_ddl

class ParsingEngine:
    def __init__(self):
        """
        Initializes the ParsingEngine.
        In a more complex setup, parsers and adapters might be registered dynamically
        or loaded based on configuration.
        """
        # Example of how parsers and adapters could be managed:
        # self.parsers = {
        #     "json": parse_json_input,
        #     # "sql": sql_parser.parse, # Assuming an SQLParser class or module
        # }
        # self.adapters = {
        #     "mysql": convert_isr_to_mysql_ddl,
        #     # "postgresql": convert_isr_to_postgres_ddl,
        # }
        pass

    def generate_schema_from_input(self, input_data: str, input_type: str) -> SchemaISR:
        """
        Processes the input data and generates an Intermediate Schema Representation (ISR).

        Args:
            input_data: The raw input string (e.g., SQL DDL, JSON, natural language text).
            input_type: A string indicating the type of input (e.g., "sql", "json", "text").

        Returns:
            An instance of SchemaISR representing the generated schema.

        Raises:
            NotImplementedError: If no parser is available for the specified input_type.
            ValueError: If the input data is invalid for the specified parser.
        """
        print(f"ParsingEngine: Received call to generate_schema_from_input for type '{input_type}'")

        normalized_input_type = input_type.lower()

        if normalized_input_type == "json":
            try:
                return parse_json_input(input_data)
            except ValueError as e:
                # Log the error or wrap it in a custom engine exception
                print(f"Error during JSON parsing: {e}")
                raise # Re-raise to be handled by the caller (e.g., API layer)
        # Add other parsers here as they are implemented
        # elif normalized_input_type == "sql":
        #     raise NotImplementedError("SQL parser is not yet implemented.")
        else:
            raise NotImplementedError(f"Parser for input type '{input_type}' is not implemented.")

    def convert_isr_to_target_ddl(self, isr: SchemaISR, target_db: str) -> str:
        """
        Converts an Intermediate Schema Representation (ISR) to a target database DDL string.

        Args:
            isr: The SchemaISR object to convert.
            target_db: A string indicating the target database (e.g., "mysql", "postgresql").

        Returns:
            A string containing the DDL for the target database.

        Raises:
            NotImplementedError: If no adapter is available for the specified target_db.
        """
        print(f"ParsingEngine: Received call to convert_isr_to_target_ddl for '{target_db}'")

        normalized_target_db = target_db.lower()

        if normalized_target_db == "mysql":
            return convert_isr_to_mysql_ddl(isr)
        # Add other adapters here
        # elif normalized_target_db == "postgresql":
        #     raise NotImplementedError("PostgreSQL adapter is not yet implemented.")
        else:
            raise NotImplementedError(f"Adapter for target database '{target_db}' is not implemented.")

# Example Usage (for direct testing of this module)
if __name__ == '__main__':
    engine = ParsingEngine()

    sample_json_input = """
    {
        "schema_name": "LibraryDB",
        "version": "v2",
        "tables": [
            {
                "name": "Books",
                "comment": "Stores book information",
                "columns": [
                    {"name": "book_id", "generic_type": "INTEGER", "constraints": [{"type": "PRIMARY_KEY"}, {"type": "AUTO_INCREMENT"}]},
                    {"name": "title", "generic_type": "STRING", "constraints": [{"type": "NOT_NULL"}]},
                    {"name": "author_id", "generic_type": "INTEGER",
                     "constraints": [
                         {"type": "FOREIGN_KEY", "details": {"references_table": "Authors", "references_columns": ["author_id"], "name": "fk_book_author"}}
                     ]
                    },
                    {"name": "status", "generic_type": "ENUM_TYPE",
                     "constraints": [
                         {"type": "ENUM_VALUES", "details": {"values": ["available", "loaned", "damaged"]}},
                         {"type": "DEFAULT", "details": {"value": "available"}}
                     ]
                    }
                ]
            },
            {
                "name": "Authors",
                "columns": [
                    {"name": "author_id", "generic_type": "INTEGER", "constraints": [{"type": "PRIMARY_KEY"}, {"type": "AUTO_INCREMENT"}]},
                    {"name": "author_name", "generic_type": "STRING", "constraints": [{"type": "NOT_NULL"}]}
                ]
            }
        ]
    }
    """
    try:
        print("\\n--- Testing JSON parsing and MySQL DDL Conversion ---")
        intermediate_schema = engine.generate_schema_from_input(sample_json_input, "json")
        print(f"Successfully parsed JSON. Schema Name: {intermediate_schema.schema_name}, Version: {intermediate_schema.version}")

        mysql_ddl = engine.convert_isr_to_target_ddl(intermediate_schema, "mysql")
        print("\\nGenerated MySQL DDL:")
        print(mysql_ddl)

    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
    except ValueError as e:
        print(f"ValueError: {e}")

    print("\\n--- Example usage finished ---")
