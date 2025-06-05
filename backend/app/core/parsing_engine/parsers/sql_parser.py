# backend/app/core/parsing_engine/parsers/sql_parser.py

import sqlparse
from sqlparse.sql import Identifier, Function, Comparison, Parenthesis, TokenList
from sqlparse.tokens import Keyword, DDL, Name, Punctuation, Literal, String, Number
from typing import List, Dict, Any, Tuple, Optional

from ..intermediate_schema import SchemaISR, TableISR, ColumnISR, ConstraintDetail

def _clean_identifier(identifier: str) -> str:
    """Removes common quotes from SQL identifiers."""
    return identifier.strip("`'\"")

def _map_sql_type_to_generic(sql_type: str, type_params: Optional[List[str]] = None) -> str:
    """Maps SQL type (base name) to a generic ISR type."""
    sql_type_upper = _clean_identifier(sql_type).upper()

    # More specific types first
    if "BIGINT" in sql_type_upper: return "BIG_INTEGER"
    if "INT" in sql_type_upper: return "INTEGER" # Catches INT, INTEGER, SMALLINT, TINYINT
    if "TEXT" in sql_type_upper or "CLOB" in sql_type_upper: return "TEXT"
    if sql_type_upper.startswith("VARCHAR") or sql_type_upper.startswith("CHAR") or \
       sql_type_upper.startswith("STRING") or sql_type_upper.startswith("NVARCHAR"): return "STRING"
    if "DECIMAL" in sql_type_upper or "NUMERIC" in sql_type_upper: return "DECIMAL"
    if "FLOAT" in sql_type_upper or "REAL" in sql_type_upper or "DOUBLE" in sql_type_upper: return "FLOAT"
    if "DATETIME" == sql_type_upper : return "DATETIME" # Exact match
    if "TIMESTAMP" in sql_type_upper: return "TIMESTAMP"
    if "DATE" == sql_type_upper: return "DATE" # Exact match
    if "TIME" == sql_type_upper and "TIMESTAMP" not in sql_type_upper : return "TIME" # Exact match
    if "BOOL" in sql_type_upper: return "BOOLEAN"
    if "BLOB" in sql_type_upper or "BINARY" in sql_type_upper or "BYTEA" in sql_type_upper: return "BLOB"
    if "JSON" in sql_type_upper: return "JSON_TYPE" # JSON, JSONB
    if "UUID" in sql_type_upper: return "UUID_TYPE"

    # print(f"Warning: Unmapped SQL type '{sql_type_upper}'. Defaulting to STRING.")
    return "STRING" # Default fallback

def _extract_column_details(tokens: List[Any]) -> Tuple[Optional[str], Optional[str], List[str], List[ConstraintDetail]]:
    """
    Extracts column name, SQL type string, type parameters, and constraints from a list of tokens.
    This is a simplified parser for column definitions.
    """
    name, sql_type_full = None, None
    type_params: List[str] = []
    constraints: List[ConstraintDetail] = []

    idx = 0

    # First token is usually the column name
    if idx < len(tokens) and isinstance(tokens[idx], (Identifier, TokenList, sqlparse.sql.Token)) and tokens[idx].ttype not in Keyword:
        name = _clean_identifier(str(tokens[idx]))
        idx += 1

    # Next is the type
    if idx < len(tokens):
        type_token = tokens[idx]
        # Type can be a Keyword (INT), Identifier (custom_type), or Function (VARCHAR(255))
        if type_token.ttype in Keyword or isinstance(type_token, (Identifier, Function)):
            sql_type_full = str(type_token)
            # Check for type parameters like VARCHAR(255)
            if isinstance(type_token, Function) and type_token.get_parameters():
                # sqlparse makes parameters part of the Function token itself
                pass # Handled by _extract_type_and_params later
            elif idx + 1 < len(tokens) and isinstance(tokens[idx+1], Parenthesis):
                # For types like DECIMAL (10, 2) where (10,2) is a separate Parenthesis token
                param_str = str(tokens[idx+1]).strip("()")
                type_params = [p.strip() for p in param_str.split(",")]
                sql_type_full += f"({param_str})" # Append for logging/original type storage
                idx += 1 # Consume the Parenthesis token
            idx += 1

    # Parse constraints from remaining tokens
    while idx < len(tokens):
        token = tokens[idx]
        token_value = str(token).upper()

        if token_value == "NOT" and idx + 1 < len(tokens) and str(tokens[idx+1]).upper() == "NULL":
            constraints.append(ConstraintDetail({"type": "NOT_NULL"}))
            idx += 2
            continue
        elif token_value == "NULL": # Usually default, handled by absence of NOT NULL
            idx += 1
            continue
        elif token_value == "PRIMARY" and idx + 1 < len(tokens) and str(tokens[idx+1]).upper() == "KEY":
            constraints.append(ConstraintDetail({"type": "PRIMARY_KEY"}))
            # Check for AUTO_INCREMENT (MySQL specific often here)
            if idx + 2 < len(tokens) and str(tokens[idx+2]).upper() == "AUTO_INCREMENT":
                constraints.append(ConstraintDetail({"type": "AUTO_INCREMENT"}))
                idx += 1 # for AUTO_INCREMENT
            idx += 2
            continue
        elif token_value == "UNIQUE":
            constraints.append(ConstraintDetail({"type": "UNIQUE"}))
            idx += 1
            continue
        elif token_value == "AUTO_INCREMENT" or token_value == "AUTOINCREMENT": # SQLite
             constraints.append(ConstraintDetail({"type": "AUTO_INCREMENT"}))
             idx += 1
             continue
        elif token_value == "DEFAULT":
            idx += 1
            if idx < len(tokens):
                default_val_token = tokens[idx]
                default_value_str = _clean_identifier(str(default_val_token))

                # Attempt to convert to actual type if it's a number or boolean keyword
                actual_default_value: Any = default_value_str
                if default_val_token.ttype in (Number.Integer, Number.Float):
                    actual_default_value = float(default_value_str) if '.' in default_value_str else int(default_value_str)
                elif default_value_str.upper() == "TRUE": actual_default_value = True
                elif default_value_str.upper() == "FALSE": actual_default_value = False
                # Keep as string for CURRENT_TIMESTAMP or other keywords/functions

                constraints.append(ConstraintDetail({"type": "DEFAULT", "details": {"value": actual_default_value}}))
                idx += 1
            continue
        # TODO: Add more constraint parsing: CHECK, FOREIGN KEY (inline)
        # These are more complex as they can involve expressions or references.
        else:
            # print(f"Skipping unhandled column token: {token} ({token.ttype})")
            idx += 1 # Move to next token if not recognized as a constraint part

    return name, sql_type_full, type_params, constraints


def _parse_table_elements(tokens_in_parenthesis: List[Any]) -> Tuple[List[ColumnISR], List[ConstraintDetail]]:
    """
    Parses elements within the CREATE TABLE parentheses (column definitions and table-level constraints).
    """
    columns_isr: List[ColumnISR] = []
    table_constraints_isr: List[ConstraintDetail] = [] # For table-level PK, FK, UNIQUE, CHECK

    # Split elements by comma, respecting parentheses for function calls or sub-queries if any
    # This is a common way sqlparse structures things: a list of Identifiers or IdentifierLists

    # A simple approach: iterate through tokens and group by top-level commas
    current_element_tokens: List[Any] = []
    paren_level = 0

    for token in tokens_in_parenthesis:
        if token.is_whitespace or (token.ttype is Punctuation and str(token) in ['(', ')'] and paren_level == 0 and not current_element_tokens):
            # Skip leading/trailing parens of the main definition block or empty tokens
            continue

        if str(token) == '(': paren_level += 1
        elif str(token) == ')': paren_level -= 1

        if token.ttype is Punctuation and str(token) == ',' and paren_level == 0:
            if current_element_tokens:
                # Process current_element_tokens as either a column or table constraint
                # For now, assume column; table constraint logic needs to be more robust
                col_name, sql_type, type_p, constrs = _extract_column_details(current_element_tokens)
                if col_name and sql_type:
                    base_sql_type, actual_type_params = _extract_type_and_params(sql_type)
                    if not type_p: type_p = actual_type_params # Use params from full type if not found separately
                    generic_type = _map_sql_type_to_generic(base_sql_type, type_p)
                    columns_isr.append(ColumnISR(name=col_name, generic_type=generic_type, constraints=constrs))
                # TODO: Else, if not a valid column, try parsing as table-level constraint
                # e.g., PRIMARY KEY (col1, col2), CONSTRAINT fk_name FOREIGN KEY ...
                current_element_tokens = []
        else:
            if not (token.is_whitespace or token.is_comment):
                current_element_tokens.append(token)

    # Process the last element
    if current_element_tokens:
        col_name, sql_type, type_p, constrs = _extract_column_details(current_element_tokens)
        if col_name and sql_type:
            base_sql_type, actual_type_params = _extract_type_and_params(sql_type)
            if not type_p: type_p = actual_type_params
            generic_type = _map_sql_type_to_generic(base_sql_type, type_p)
            columns_isr.append(ColumnISR(name=col_name, generic_type=generic_type, constraints=constrs))
        # TODO: Else, parse as table-level constraint

    return columns_isr, table_constraints_isr


def parse_sql_ddl_input(sql_ddl: str) -> SchemaISR:
    parsed_statements = sqlparse.parse(sql_ddl)
    tables_isr: List[TableISR] = []
    schema_name: Optional[str] = None

    for stmt in parsed_statements:
        if stmt.get_type() != 'CREATE':
            continue

        tokens = [t for t in stmt.tokens if not t.is_whitespace and not t.is_comment]

        token_idx = 0
        if not (tokens[token_idx].match(DDL, 'CREATE')): continue
        token_idx += 1

        # Skip optional keywords like OR REPLACE, TEMPORARY
        while token_idx < len(tokens) and tokens[token_idx].is_keyword and \
              str(tokens[token_idx]).upper() not in ['TABLE', 'VIEW', 'INDEX', 'DATABASE', 'SCHEMA']:
            token_idx +=1

        if token_idx >= len(tokens) or not tokens[token_idx].match(Keyword, 'TABLE'):
            continue # Not a CREATE TABLE statement
        token_idx += 1

        if token_idx < len(tokens) and tokens[token_idx].match(Keyword, 'IF NOT EXISTS'):
            token_idx += 1

        if token_idx >= len(tokens) or not isinstance(tokens[token_idx], (Identifier, TokenList)): # Table name can be TokenList if quoted multipart
            # print(f"Warning: Could not parse table name from statement: {stmt}")
            continue

        table_name = _clean_identifier(str(tokens[token_idx].get_real_name() if hasattr(tokens[token_idx], 'get_real_name') else str(tokens[token_idx])))
        token_idx += 1

        column_defs_parenthesis: Optional[Parenthesis] = None
        for t in tokens[token_idx:]:
            if isinstance(t, Parenthesis):
                column_defs_parenthesis = t
                break

        if not column_defs_parenthesis:
            # print(f"Warning: Could not find column definitions for table '{table_name}'.")
            continue

        # Get tokens within the main parenthesis, excluding the parenthesis themselves and leading/trailing whitespace
        inner_column_def_tokens = [t for t in column_defs_parenthesis.tokens if not t.is_whitespace and str(t) not in ('(',')')]

        columns_isr, table_constraints_isr = _parse_table_elements(inner_column_def_tokens)

        # TODO: Process table_constraints_isr and potentially update columns_isr (e.g., mark PK from table constraint)
        # For now, we only use column-level parsed constraints.

        if columns_isr: # Only add table if it has successfully parsed columns
            tables_isr.append(TableISR(name=table_name, columns=columns_isr))
        # TODO: Handle ALTER TABLE statements to add constraints after table creation.

    return SchemaISR(tables=tables_isr, schema_name=schema_name)
