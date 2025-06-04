# backend/app/core/parsing_engine/intermediate_schema.py
from typing import List, Optional, Any, Dict

class ColumnISR:
    def __init__(self, name: str, generic_type: str):
        self.name = name
        self.generic_type = generic_type
        self.constraints = []
        self.comment = None

class TableISR:
    def __init__(self, name: str, columns: List[ColumnISR]):
        self.name = name
        self.columns = columns
        self.comment = None

class SchemaISR:
    def __init__(self, tables: List[TableISR]):
        self.schema_name = None
        self.version = None
        self.tables = tables
