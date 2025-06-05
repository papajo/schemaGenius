# Refinement of python_orm_parser.py to better handle ForeignKeys and Enums

import ast
from typing import List, Dict, Any, Optional, Union

from ..intermediate_schema import SchemaISR, TableISR, ColumnISR, ConstraintDetail

def _map_sqlalchemy_type_to_generic(sqla_type_name: str, type_args: Optional[List[Any]] = None) -> str:
    # This function remains largely the same as previously defined,
    # focusing on mapping SQLAlchemy type names (like "String", "Integer")
    # to generic ISR types ("STRING", "INTEGER").
    # It's important for this to be as comprehensive as possible for common SQLAlchemy types.
    sqla_type_upper = sqla_type_name.upper()
    if sqla_type_upper in ["INTEGER", "SMALLINTEGER", "BIGINTEGER", "INT"]:
        if "BIGINTEGER" in sqla_type_upper or "BIGINT" in sqla_type_upper: return "BIG_INTEGER"
        return "INTEGER"
    if sqla_type_upper in ["STRING", "TEXT", "UNICODE", "UNICODETEXT", "NVARCHAR", "VARCHAR", "CHAR"]:
        if "TEXT" in sqla_type_upper or "CLOB" in sqla_type_upper: return "TEXT"
        return "STRING"
    if sqla_type_upper in ["FLOAT", "REAL", "DOUBLE_PRECISION", "DOUBLE"]: return "FLOAT"
    if sqla_type_upper == "NUMERIC" or sqla_type_upper == "DECIMAL": return "DECIMAL"
    if sqla_type_upper == "BOOLEAN" or sqla_type_upper == "BOOL": return "BOOLEAN"
    if sqla_type_upper == "DATE": return "DATE"
    if sqla_type_upper == "DATETIME": return "DATETIME"
    if sqla_type_upper == "TIMESTAMP": return "TIMESTAMP"
    if sqla_type_upper in ["BLOB", "BINARY", "LARGEBINARY", "VARBINARY", "BYTEA"]: return "BLOB"
    if sqla_type_upper == "JSON": return "JSON_TYPE"
    if sqla_type_upper == "UUID": return "UUID_TYPE"
    if sqla_type_upper == "ENUM": return "ENUM_TYPE" # The visitor will handle extracting values
    return "STRING" # Default fallback

class SQLAlchemyModelVisitor(ast.NodeVisitor):
    def __init__(self, base_class_names=None, sqla_module_aliases=None):
        self.tables_isr: List[TableISR] = []
        self._current_table_columns: List[ColumnISR] = []
        self._current_table_name: Optional[str] = None
        self.base_class_names = base_class_names if base_class_names else {"Base", "DeclarativeBase", "Model", "BaseModel"} # Added BaseModel
        self.sqla_module_aliases = sqla_module_aliases if sqla_module_aliases else {"sa", "orm", "sqlalchemy", "db", "so"} # Added so

    def _is_sqlalchemy_base(self, node: ast.ClassDef) -> bool:
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id in self.base_class_names: return True
            if isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name) and \
               base.value.id in self.sqla_module_aliases and base.attr == "Model": return True
        return False

    def _get_ast_literal_value(self, node: Optional[ast.AST]) -> Any:
        if node is None: return None
        if isinstance(node, ast.Constant): return node.value
        if isinstance(node, ast.Str): return node.s # Python < 3.8
        if isinstance(node, ast.Num): return node.n # Python < 3.8
        if isinstance(node, ast.NameConstant): return node.value # True, False, None
        if isinstance(node, ast.List): return [self._get_ast_literal_value(e) for e in node.elts]
        if isinstance(node, ast.Tuple): return tuple(self._get_ast_literal_value(e) for e in node.elts)
        # For ast.Name (variables) or ast.Call (function calls), static evaluation is hard.
        # Return a representation or a specific marker if needed.
        # For now, returning a string representation for unhandled complex types.
        return f"AST_NODE:{type(node).__name__}"


    def visit_ClassDef(self, node: ast.ClassDef):
        if not self._is_sqlalchemy_base(node):
            self.generic_visit(node) # Visit children for other potential definitions
            return

        original_table_name = self._current_table_name # Store for nested class safety
        original_columns = self._current_table_columns

        self._current_table_name = node.name # Default to class name
        self._current_table_columns = []
        table_comment = ast.get_docstring(node)

        for item in node.body:
            if isinstance(item, ast.Assign):
                if len(item.targets) == 1 and isinstance(item.targets[0], ast.Name) and item.targets[0].id == "__tablename__":
                    val = self._get_ast_literal_value(item.value)
                    if isinstance(val, str): self._current_table_name = val
            elif isinstance(item, (ast.Assign, ast.AnnAssign)):
                self._parse_column_assignment(item)
            # TODO: Parse __table_args__ for table-level constraints (UniqueConstraint, Index, etc.)

        if self._current_table_name and self._current_table_columns:
            self.tables_isr.append(TableISR(name=self._current_table_name, columns=self._current_table_columns, comment=table_comment))

        self.generic_visit(node) # Visit children for nested classes (though less common for models)

        self._current_table_name = original_table_name # Restore context
        self._current_table_columns = original_columns


    def _parse_column_assignment(self, node: Union[ast.Assign, ast.AnnAssign]):
        col_name: Optional[str] = None
        if isinstance(node.target, ast.Name): col_name = node.target.id # AnnAssign
        elif isinstance(node.targets[0], ast.Name): col_name = node.targets[0].id # Assign
        if not col_name or not node.value or not isinstance(node.value, ast.Call): return

        # Check if function call is Column, mapped_column, ForeignKey, Enum etc.
        func_node = node.value.func
        is_col_def_call = False
        # Check for sa.Column, db.Column, Column, sa.mapped_column, mapped_column
        if isinstance(func_node, ast.Name) and func_node.id in ["Column", "mapped_column"]: is_col_def_call = True
        elif isinstance(func_node, ast.Attribute) and isinstance(func_node.value, ast.Name) and \
             func_node.value.id in self.sqla_module_aliases and func_node.attr in ["Column", "mapped_column"]:
            is_col_def_call = True

        if not is_col_def_call: return # Not a column definition we parse directly here

        generic_type, constraints_isr, col_comment = "STRING", [], None # Defaults

        # 1. Type from Annotation (for Mapped[type])
        if isinstance(node, ast.AnnAssign) and node.annotation:
            ann_node = node.annotation
            if isinstance(ann_node, ast.Subscript) and isinstance(ann_node.value, ast.Name) and \
               ann_node.value.id in ["Mapped", "Optional"]: # Mapped[int] or Optional[int]
                ann_node = ann_node.slice # Get the actual type node

            if isinstance(ann_node, ast.Name): # e.g. int, str, MyCustomEnum
                py_type_name = ann_node.id
                # Basic Python type mapping
                if py_type_name == "int": generic_type = "INTEGER"
                elif py_type_name == "str": generic_type = "STRING"
                elif py_type_name == "float": generic_type = "FLOAT"
                elif py_type_name == "bool": generic_type = "BOOLEAN"
                elif py_type_name == "datetime": generic_type = "DATETIME" # from datetime.datetime
                # If it's a custom type (like a Python Enum used in SQLAlchemy Enum), it might be ENUM_TYPE
                # This requires more context or checking if this name is an Enum class defined elsewhere.
                # For now, if not a basic python type, it might be an SQLAlchemy type directly or an Enum.
                else: generic_type = _map_sqlalchemy_type_to_generic(py_type_name)

            elif isinstance(ann_node, ast.Attribute) and isinstance(ann_node.value, ast.Name): # e.g. sqlalchemy.Integer, types.Integer
                # Assuming ann_node.value.id is an alias like 'sa' or 'types'
                sqla_type_name = ann_node.attr # e.g. Integer
                generic_type = _map_sqlalchemy_type_to_generic(sqla_type_name)


        # 2. Type from Column/mapped_column first argument (can override or specify details)
        type_arg_node: Optional[ast.AST] = None
        if node.value.args: type_arg_node = node.value.args[0]

        # Handle ForeignKey specifically as it's often the first arg and implies type from related col
        is_foreign_key_type = False
        if type_arg_node and isinstance(type_arg_node, ast.Call):
            fk_func_node = type_arg_node.func
            is_fk_call = False
            if isinstance(fk_func_node, ast.Name) and fk_func_node.id == "ForeignKey": is_fk_call = True
            elif isinstance(fk_func_node, ast.Attribute) and fk_func_node.attr == "ForeignKey": is_fk_call = True

            if is_fk_call and type_arg_node.args:
                is_foreign_key_type = True
                fk_target_node = type_arg_node.args[0]
                fk_target = self._get_ast_literal_value(fk_target_node)
                if isinstance(fk_target, str) and "." in fk_target:
                    ref_table, ref_col = fk_target.split(".", 1)
                    # Type of FK column is usually INTEGER or matches the referenced PK type.
                    # For now, default to INTEGER if not specified by annotation.
                    if generic_type == "STRING" or generic_type == "UNKNOWN_TYPE": # If type wasn't well inferred from annotation
                         generic_type = "INTEGER"
                    constraints_isr.append(ConstraintDetail({"type": "FOREIGN_KEY", "details": {"references_table": ref_table, "references_column": ref_col}}))

        if not is_foreign_key_type and type_arg_node: # If not FK, then it's a type definition
            sqla_type_name, type_params_vals = "", []
            if isinstance(type_arg_node, ast.Name): sqla_type_name = type_arg_node.id
            elif isinstance(type_arg_node, ast.Attribute) and isinstance(type_arg_node.value, ast.Name):
                sqla_type_name = f"{type_arg_node.value.id}.{type_arg_node.attr}" # For sa.String, etc.
            elif isinstance(type_arg_node, ast.Call): # String(50) or sa.String(50) or Enum("a","b")
                type_func = type_arg_node.func
                if isinstance(type_func, ast.Name): sqla_type_name = type_func.id
                elif isinstance(type_func, ast.Attribute) and isinstance(type_func.value, ast.Name):
                     sqla_type_name = f"{type_func.value.id}.{type_func.attr}"

                type_params_vals = [self._get_ast_literal_value(arg) for arg in type_arg_node.args]

            if sqla_type_name:
                # This type from arg is more specific, so it takes precedence
                generic_type = _map_sqlalchemy_type_to_generic(sqla_type_name, type_params_vals)
                if generic_type == "ENUM_TYPE" and type_params_vals:
                    # Assuming values are passed directly to Enum constructor
                    enum_actual_values = [v for v in type_params_vals if isinstance(v, str)]
                    if enum_actual_values:
                        constraints_isr.append(ConstraintDetail({"type": "ENUM_VALUES", "details": {"values": enum_actual_values}}))


        # 3. Constraints from keyword arguments
        for kw in node.value.keywords:
            val = self._get_ast_literal_value(kw.value)
            if kw.arg == "primary_key" and val is True: constraints_isr.append(ConstraintDetail({"type": "PRIMARY_KEY"}))
            elif kw.arg == "nullable" and val is False: constraints_isr.append(ConstraintDetail({"type": "NOT_NULL"}))
            elif kw.arg == "unique" and val is True: constraints_isr.append(ConstraintDetail({"type": "UNIQUE"}))
            elif kw.arg == "autoincrement" and val is True: constraints_isr.append(ConstraintDetail({"type": "AUTO_INCREMENT"}))
            elif kw.arg == "default" and val is not None : constraints_isr.append(ConstraintDetail({"type": "DEFAULT", "details": {"value": val}}))
            elif kw.arg == "comment" and isinstance(val, str): col_comment = val
            # Handle ForeignKey defined as a keyword argument (less common for Column, more for mapped_column)
            elif kw.arg == "foreign_key" and isinstance(val, str) and "." in val: # foreign_key='users.id'
                ref_table, ref_col = val.split(".", 1)
                constraints_isr.append(ConstraintDetail({"type": "FOREIGN_KEY", "details": {"references_table": ref_table, "references_column": ref_col}}))

        self._current_table_columns.append(ColumnISR(name=col_name, generic_type=generic_type, constraints=constraints_isr, comment=col_comment))


def parse_python_orm_input(python_code: str, orm_type: str = "sqlalchemy") -> SchemaISR:
    if orm_type.lower() != "sqlalchemy": raise NotImplementedError(f"ORM type {orm_type} not supported.")
    try: parsed_ast = ast.parse(python_code)
    except SyntaxError as e: raise ValueError(f"Invalid Python syntax: {e}")

    visitor = SQLAlchemyModelVisitor(
        base_class_names={"Base", "DeclarativeBase", "Model", "BaseModel"}, # Common base class names
        sqla_module_aliases={"sa", "db", "orm", "sqlalchemy", "so"} # Common module aliases
    )
    visitor.visit(parsed_ast)
    return SchemaISR(tables=visitor.tables_isr)

# Example usage (kept for direct testing, will be removed or conditionalized for production)
if __name__ == '__main__':
    # ... (previous example code can be used here for testing)
    pass
