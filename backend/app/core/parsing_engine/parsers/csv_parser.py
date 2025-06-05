# backend/app/core/parsing_engine/parsers/csv_parser.py

import csv
import io # For treating string as a file
from typing import List, Optional, Any

from ..intermediate_schema import SchemaISR, TableISR, ColumnISR, ConstraintDetail # ConstraintDetail might not be used here yet

def _clean_csv_header(header_name: str) -> str:
    """Cleans a CSV header name to be a valid and more standard identifier."""
    if not header_name:
        return "unnamed_column"
    name = header_name.strip().strip("'\"") # Remove surrounding quotes and whitespace
    # Replace spaces and common special characters with underscores
    name = name.replace(" ", "_").replace("-", "_").replace(".", "_").replace("/", "_")
    # Remove any other non-alphanumeric characters (except underscore) that might remain
    name = ''.join(c for c in name if c.isalnum() or c == '_')
    # Ensure it doesn't start with a number (prepend underscore if so)
    if name and name[0].isdigit():
        name = "_" + name
    # Handle potential multiple underscores from replacements
    name = "_".join(filter(None, name.split('_')))
    return name if name else "unnamed_column"


def _infer_column_type(values: List[str], sample_size: int = 100) -> str:
    """
    Infers the generic type of a column based on a sample of its values.
    This is a basic type inference. Can be significantly improved.
    """
    is_int = True
    is_float = True
    is_bool = True

    # Consider only non-empty, non-None values from the sample for actual type detection
    # If all values are empty/None in the sample, it defaults to STRING.
    sampled_values = [v for v in values if v is not None and v.strip()][:sample_size]

    if not sampled_values:
        return "STRING"

    bool_keywords = {"true", "false", "yes", "no", "t", "f", "y", "n", "1", "0", "on", "off"}

    for value_str in sampled_values:
        value_str_lower = value_str.lower()

        # Integer check
        if is_int:
            try:
                int(value_str)
            except ValueError:
                is_int = False

        # Float check (A value could be int and also float, but if it failed int, it might still be float)
        if is_float: # Check float independently of int success/failure for this value
            try:
                float(value_str)
            except ValueError:
                is_float = False

        # Boolean check
        if is_bool and value_str_lower not in bool_keywords:
            is_bool = False

        # Optimization: If all types are already false for this column, no need to check further values.
        if not is_int and not is_float and not is_bool:
            break

    # Type precedence: INTEGER -> FLOAT -> BOOLEAN -> STRING
    # If all sampled values are integers, it's INTEGER.
    # If all are integers OR floats (but not all are strictly integers), it's FLOAT.
    # If all are booleans (and not fitting int/float more generally), it's BOOLEAN.
    if is_int: return "INTEGER"  # All sampled values were parseable as int
    if is_float: return "FLOAT" # All sampled values were parseable as float (includes integers)
    if is_bool: return "BOOLEAN"

    return "STRING" # Default if no other type fits consistently


def parse_csv_input(csv_data: str, table_name_from_file: Optional[str] = None) -> SchemaISR:
    """
    Parses CSV data from a string into a SchemaISR object, inferring column names and types.
    Assumes the first row is the header.

    Args:
        csv_data: A string containing the CSV data.
        table_name_from_file: An optional name for the table, often derived from the CSV filename.

    Returns:
        A SchemaISR object containing a single table definition.
        Returns an empty SchemaISR if CSV is empty.

    Raises:
        ValueError: If CSV data is malformed or header is missing/empty.
    """
    effective_table_name = _clean_csv_header(table_name_from_file) if table_name_from_file else "csv_imported_table"

    file_like_object = io.StringIO(csv_data)

    try:
        # Sniff dialect to handle CSVs with different delimiters, quote chars, etc.
        # Read a sample for sniffing, then reset the stream.
        sample = file_like_object.read(2048) # Read a larger sample for better sniffing
        file_like_object.seek(0) # Reset stream position

        # If sample is empty or just whitespace, treat as empty CSV
        if not sample.strip():
             return SchemaISR(tables=[])

        dialect = csv.Sniffer().sniff(sample)
        reader = csv.reader(file_like_object, dialect)
    except csv.Error as e:
        # Fallback to standard dialect if sniffing fails on very small/simple CSVs
        try:
            file_like_object.seek(0)
            reader = csv.reader(file_like_object)
        except csv.Error as e_fallback:
             raise ValueError(f"Error parsing CSV data: {e_fallback} (Sniffing also failed: {e})")


    rows = list(reader)

    if not rows:
        return SchemaISR(tables=[]) # Empty CSV

    header = rows[0]
    if not any(h.strip() for h in header): # Check if all header cells are empty or whitespace
        raise ValueError("CSV header row is missing, empty, or contains only whitespace.")

    column_names = [_clean_csv_header(h) for h in header]

    # Handle duplicate column names by appending a suffix
    final_column_names: List[str] = []
    name_counts: Dict[str, int] = {}
    for name in column_names:
        if name in name_counts:
            name_counts[name] += 1
            final_column_names.append(f"{name}_{name_counts[name]}")
        else:
            name_counts[name] = 0 # First occurrence
            final_column_names.append(name)
    column_names = final_column_names

    data_rows = rows[1:]
    if not data_rows:
        # Only header row was present, create table with STRING type for all columns
        columns_isr = [ColumnISR(name=name, generic_type="STRING") for name in column_names]
        table_isr = TableISR(name=effective_table_name, columns=columns_isr)
        return SchemaISR(tables=[table_isr])

    # Transpose data for column-wise type inference
    # Initialize with empty lists for each column
    columns_data: List[List[str]] = [[] for _ in range(len(column_names))]
    for row in data_rows:
        for i, cell_value in enumerate(row):
            if i < len(column_names): # Ensure we don't go out of bounds if a row is shorter
                columns_data[i].append(cell_value)
            # If a row is longer than header, extra cells are ignored.

    columns_isr: List[ColumnISR] = []
    for i, col_name in enumerate(column_names):
        col_values = columns_data[i] if i < len(columns_data) else []
        generic_type = _infer_column_type(col_values)
        # Constraints are not typically inferred from CSV directly.
        # One might infer NOT NULL if a column has no empty values in a large sample, but this is risky.
        columns_isr.append(ColumnISR(name=col_name, generic_type=generic_type))

    table_isr = TableISR(name=effective_table_name, columns=columns_isr)
    return SchemaISR(tables=[table_isr])


# Example usage:
if __name__ == '__main__':
    sample_csv_data_standard = """ID,Name,Age,IsActive,Value,Notes,Date Joined
1,Alice,30,true,100.5,First entry,2023-01-15
2,Bob,24,false,200,,2022-11-30
3,Charlie,,yes,,"Third, with comma",
4,David,35,T,30.25,,"2024-03-01"
5,,40,0,10.0,Empty Name,
"""
    malformed_csv_data = """ID;Name;Age\n1;Test;""" # Missing value, potentially bad delimiter for default reader

    print("--- Testing CSV Parser with Standard CSV ---")
    try:
        schema = parse_csv_input(sample_csv_data_standard, table_name_from_file="Sample Users Data")
        if schema.tables:
            table = schema.tables[0]
            print(f"Table Name: {table.name}")
            for col in table.columns:
                print(f"  Column: {_clean_csv_header(col.name)}, Type: {col.generic_type}")
        else:
            print("No tables parsed from CSV.")
    except ValueError as e:
        print(f"Error: {e}")

    print("\\n--- Testing CSV Parser with only header ---")
    header_only_csv = "ID,Name,Email"
    try:
        schema_ho = parse_csv_input(header_only_csv, "HeaderOnly")
        if schema_ho.tables:
            table_ho = schema_ho.tables[0]
            print(f"Table Name: {table_ho.name}")
            for col in table_ho.columns:
                 print(f"  Column: {col.name}, Type: {col.generic_type}")
        else:
            print("No tables parsed from header-only CSV.")
    except ValueError as e:
        print(f"Error: {e}")

    print("\\n--- Testing CSV Parser with empty CSV ---")
    empty_csv = ""
    try:
        schema_e = parse_csv_input(empty_csv, "EmptyFile")
        if not schema_e.tables:
            print("Correctly parsed no tables from empty CSV.")
        else:
            print("Error: Parsed tables from empty CSV.")
    except ValueError as e: # Should not raise ValueError for empty string, should return empty schema
        print(f"Error with empty CSV: {e}")

    print("\\n--- Testing CSV Parser with malformed CSV (expecting error or specific handling) ---")
    try:
        schema_mf = parse_csv_input(malformed_csv_data, "Malformed")
        # Depending on strictness, this might parse or partially parse.
        # The current implementation might succeed if sniffer or default reader manages.
        if schema_mf.tables:
            table_mf = schema_mf.tables[0]
            print(f"Table Name: {table_mf.name}")
            for col in table_mf.columns:
                 print(f"  Column: {col.name}, Type: {col.generic_type}")
        else:
            print("No tables parsed from malformed CSV.")
    except ValueError as e:
        print(f"Caught expected error for malformed CSV: {e}")

    print("\\n--- Testing CSV with duplicate headers ---")
    duplicate_header_csv = "ID,Name,ID,Name,Value"
    try:
        schema_dh = parse_csv_input(duplicate_header_csv, "DuplicateHeaders")
        if schema_dh.tables:
            table_dh = schema_dh.tables[0]
            print(f"Table Name: {table_dh.name}")
            for col in table_dh.columns:
                 print(f"  Column: {col.name}, Type: {col.generic_type}")
            # Expected: ID, Name, ID_1, Name_1, Value
            self.assertTrue(any(c.name == "ID_1" for c in table_dh.columns))
            self.assertTrue(any(c.name == "Name_1" for c in table_dh.columns))
        else:
            print("No tables parsed from duplicate header CSV.")
    except ValueError as e:
        print(f"Error: {e}")

    print("\\n--- Testing CSV with only whitespace headers ---")
    whitespace_header_csv = " ,  ,   "
    try:
        schema_wh = parse_csv_input(whitespace_header_csv, "WhitespaceHeaders")
        # Expecting a ValueError as per implementation
    except ValueError as e:
        print(f"Caught expected error for whitespace headers: {e}")

    print("\\n--- Testing CSV with numeric headers ---")
    numeric_header_csv = "1,2,3_Test\nVal1,Val2,Val3"
    try:
        schema_nh = parse_csv_input(numeric_header_csv, "NumericHeaders")
        if schema_nh.tables:
            table_nh = schema_nh.tables[0]
            print(f"Table Name: {table_nh.name}")
            self.assertTrue(any(c.name == "_1" for c in table_nh.columns)) # Check if numeric header was prefixed
            self.assertTrue(any(c.name == "_2" for c in table_nh.columns))
            self.assertTrue(any(c.name == "_3_Test" for c in table_nh.columns))
            for col in table_nh.columns:
                 print(f"  Column: {col.name}, Type: {col.generic_type}")
        else:
            print("No tables parsed from numeric header CSV.")
    except ValueError as e:
        print(f"Error: {e}")
