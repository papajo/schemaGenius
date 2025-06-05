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
from .parsers.python_orm_parser import parse_python_orm_input # Import Python ORM parser
from .adapters.mysql_adapter import convert_isr_to_mysql_ddl
from .adapters.postgresql_adapter import convert_isr_to_postgresql_ddl

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
            "python": parse_python_orm_input,       # For generic Python ORM code
            "sqlalchemy": parse_python_orm_input, # Alias for SQLAlchemy specifically
            # "text": parse_nlp_input, # Future NLP parser
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
            elif input_type_lower == "python" or input_type_lower == "sqlalchemy":
                # The python_orm_parser's second argument is orm_type, defaulting to "sqlalchemy"
                return parser_func(input_data, orm_type="sqlalchemy")
            else:
                return parser_func(input_data)
        except ValueError as ve: # Specific error from parsers (e.g., JSON format, Python Syntax)
            print(f"ValueError during '{input_type_lower}' parsing: {ve}")
            raise
        except Exception as e: # Broader exceptions
            print(f"Unexpected error during '{input_type_lower}' parsing: {type(e).__name__} - {e}")
            raise ValueError(f"Error processing '{input_type_lower}' input: {e}")

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
            print(f"Unexpected error during DDL conversion for '{target_db_lower}': {type(e).__name__} - {e}")
            raise ValueError(f"Error converting ISR to DDL for '{target_db_lower}': {e}")

# Example Usage (for direct testing of this module)
if __name__ == '__main__':
    engine = ParsingEngine()
    sample_python_code = """
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
Base = declarative_base()
class OrmTest(Base):
    __tablename__ = "orm_table"
    id = Column(Integer, primary_key=True)
    data = Column(String)
"""
    try:
        print("\\n--- Testing Python ORM input to MySQL DDL ---")
        intermediate_schema_orm = engine.generate_schema_from_input(sample_python_code, "python")
        print(f"Parsed Python ORM: Found {len(intermediate_schema_orm.tables)} table(s).")
        if intermediate_schema_orm.tables:
            print(f"  Table Name: {intermediate_schema_orm.tables[0].name}")

        mysql_ddl_from_orm = engine.convert_isr_to_target_ddl(intermediate_schema_orm, "mysql")
        print("MySQL DDL from Python ORM input:\n", mysql_ddl_from_orm)
    except Exception as e:
        print(f"Error in Python ORM processing: {e}")

    print("\\n--- Example usage finished ---")
