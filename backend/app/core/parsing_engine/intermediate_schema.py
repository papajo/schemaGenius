# backend/app/core/parsing_engine/intermediate_schema.py
from typing import List, Optional, Any, Dict

class ConstraintDetail:
    def __init__(self, constraint_data: Dict[str, Any]):
        self.type: Optional[str] = constraint_data.get("type")
        # Example: For a FOREIGN KEY, details might include:
        # "references_table": "other_table", "references_columns": ["id"]
        # For a CHECK constraint, details might include:
        # "condition": "value > 0"
        self.details: Dict[str, Any] = constraint_data

    def __repr__(self) -> str:
        return f"ConstraintDetail(type={self.type}, details={self.details})"

class ColumnISR:
    def __init__(self, name: str, generic_type: str, constraints: Optional[List[ConstraintDetail]] = None, comment: Optional[str] = None):
        self.name = name
        self.generic_type = generic_type
        self.constraints: List[ConstraintDetail] = constraints if constraints is not None else []
        self.comment = comment

    def __repr__(self) -> str:
        return f"ColumnISR(name='{self.name}', type='{self.generic_type}', constraints={len(self.constraints)}, comment='{self.comment}')"

class TableISR:
    def __init__(self, name: str, columns: List[ColumnISR], comment: Optional[str] = None):
        self.name = name
        self.columns = columns
        self.comment = comment

    def __repr__(self) -> str:
        return f"TableISR(name='{self.name}', columns={len(self.columns)}, comment='{self.comment}')"

class SchemaISR:
    def __init__(self, tables: List[TableISR], schema_name: Optional[str] = None, version: Optional[str] = None):
        self.schema_name = schema_name
        self.version = version
        self.tables = tables

    def __repr__(self) -> str:
        return f"SchemaISR(name='{self.schema_name}', version='{self.version}', tables={len(self.tables)})"
