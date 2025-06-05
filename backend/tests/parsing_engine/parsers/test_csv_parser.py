# backend/tests/parsing_engine/parsers/test_csv_parser.py

import unittest
# Assuming tests are run from 'backend' directory or test runner handles paths
from app.core.parsing_engine.parsers.csv_parser import parse_csv_input, _infer_column_type, _clean_csv_header
from app.core.parsing_engine.intermediate_schema import SchemaISR, TableISR, ColumnISR

class TestCsvParser(unittest.TestCase):

    def test_clean_csv_header(self):
        self.assertEqual(_clean_csv_header(" First Name "), "First_Name")
        self.assertEqual(_clean_csv_header("email-address"), "email_address")
        self.assertEqual(_clean_csv_header("column.with.dots"), "column_with_dots")
        self.assertEqual(_clean_csv_header("column/with/slashes"), "column_with_slashes")
        self.assertEqual(_clean_csv_header("123_startsWithNumber"), "_123_startsWithNumber")
        self.assertEqual(_clean_csv_header("  Multiple   Spaces  "), "Multiple_Spaces")
        self.assertEqual(_clean_csv_header("test!@#col$"), "testcol") # Test special char removal
        self.assertEqual(_clean_csv_header("col1__col2_"), "col1_col2") # Test multiple underscores
        self.assertEqual(_clean_csv_header("\n \t"), "unnamed_column") # All whitespace
        self.assertEqual(_clean_csv_header(""), "unnamed_column")
        self.assertEqual(_clean_csv_header(None), "unnamed_column")


    def test_infer_column_type(self):
        self.assertEqual(_infer_column_type(["1", "2", "3", "450"]), "INTEGER")
        self.assertEqual(_infer_column_type(["1.0", "2.5", "3.14", "0.99"]), "FLOAT")
        self.assertEqual(_infer_column_type(["1", "2.5", "3", None, " "]), "FLOAT") # Mixed int/float, ignores None/empty
        self.assertEqual(_infer_column_type(["true", "false", "TRUE", "FALSE"]), "BOOLEAN")
        self.assertEqual(_infer_column_type(["T", "f", "Yes", "nO", "0", "1", "ON", "off"]), "BOOLEAN")
        self.assertEqual(_infer_column_type(["1", "0", "1"]), "BOOLEAN") # "1", "0" are strong bool indicators
        self.assertEqual(_infer_column_type(["Alice", "Bob", "Charlie"]), "STRING")
        self.assertEqual(_infer_column_type(["1", "Alice", "2.5"]), "STRING") # Mixed non-convertible
        self.assertEqual(_infer_column_type(["", None, "  "]), "STRING") # All empty/None or whitespace
        self.assertEqual(_infer_column_type(["1", "", "3", None]), "INTEGER") # Empty/None ignored if others typed
        self.assertEqual(_infer_column_type(["1.1", "", "3.3", None]), "FLOAT")
        self.assertEqual(_infer_column_type(["true", "", "false", None]), "BOOLEAN")
        self.assertEqual(_infer_column_type(["text", "true", "1"]), "STRING") # "text" makes it string


    def test_simple_csv_parsing(self):
        csv_data = "id,name,value,is_member\n1,Alice,10.5,true\n2,Bob,20.0,false\n3,Charlie,5,T"
        schema_isr = parse_csv_input(csv_data, table_name_from_file="simple_data")

        self.assertEqual(len(schema_isr.tables), 1)
        table = schema_isr.tables[0]
        self.assertEqual(table.name, "simple_data")
        self.assertEqual(len(table.columns), 4)

        expected_cols = {
            "id": "INTEGER", "name": "STRING", "value": "FLOAT", "is_member": "BOOLEAN"
        }
        for col in table.columns:
            self.assertEqual(col.generic_type, expected_cols.get(col.name))

    def test_csv_only_header(self):
        csv_data = "col_a,col_b,col_c"
        schema_isr = parse_csv_input(csv_data, "header_only_table")
        self.assertEqual(len(schema_isr.tables), 1)
        table = schema_isr.tables[0]
        self.assertEqual(table.name, "header_only_table")
        self.assertEqual(len(table.columns), 3)
        self.assertTrue(all(c.generic_type == "STRING" for c in table.columns)) # Default for no data

    def test_empty_csv_data(self):
        csv_data_empty_string = "" # Completely empty
        schema_isr_es = parse_csv_input(csv_data_empty_string)
        self.assertEqual(len(schema_isr_es.tables), 0)

        csv_data_whitespace = "   \n   \t   " # Only whitespace
        schema_isr_ws = parse_csv_input(csv_data_whitespace)
        self.assertEqual(len(schema_isr_ws.tables), 0)

    def test_csv_whitespace_header_error(self):
        csv_data = " ,  ,   \n1,2,3" # Header cells are all whitespace
        with self.assertRaisesRegex(ValueError, "CSV header row is missing, empty, or contains only whitespace."):
            parse_csv_input(csv_data)

    def test_duplicate_header_names_cleaned(self):
        csv_data = "Name,Value,Name,Other,Value\nAlice,1,Bob,X,2\nCarol,3,Dave,Y,4"
        schema_isr = parse_csv_input(csv_data, "duplicates") # Table name from file
        table = schema_isr.tables[0]
        self.assertEqual(table.name, "duplicates")
        self.assertEqual(len(table.columns), 5)
        col_names = [c.name for c in table.columns]

        self.assertIn("Name", col_names)
        self.assertIn("Name_1", col_names) # First duplicate of "Name"
        self.assertIn("Value", col_names)
        self.assertIn("Value_1", col_names) # First duplicate of "Value"
        self.assertIn("Other", col_names)

    def test_csv_with_different_delimiter_sniffing(self):
        csv_data = "id;name;active\n1;Laptop;true\n2;Mouse;false" # Semicolon delimited
        schema_isr = parse_csv_input(csv_data, "semicolon_data")
        self.assertEqual(len(schema_isr.tables), 1)
        table = schema_isr.tables[0]
        self.assertEqual(table.name, "semicolon_data")
        self.assertEqual(len(table.columns), 3)

        id_col = next(c for c in table.columns if c.name == "id")
        self.assertEqual(id_col.generic_type, "INTEGER")

        active_col = next(c for c in table.columns if c.name == "active")
        self.assertEqual(active_col.generic_type, "BOOLEAN")

    def test_csv_with_quotes_and_commas_in_data(self):
        csv_data = 'id,item_name,description\n1,"Laptop, Gaming","High-end, 17\\" screen"\n2,Mouse,"Optical, with scroll-wheel"'
        schema_isr = parse_csv_input(csv_data, "quoted_data")
        self.assertEqual(len(schema_isr.tables), 1)
        table = schema_isr.tables[0]
        self.assertEqual(len(table.columns), 3)
        self.assertEqual(table.columns[0].name, "id")
        self.assertEqual(table.columns[1].name, "item_name")
        self.assertEqual(table.columns[2].name, "description")
        # Type inference should still work
        self.assertEqual(table.columns[0].generic_type, "INTEGER")
        self.assertEqual(table.columns[1].generic_type, "STRING")
        self.assertEqual(table.columns[2].generic_type, "STRING") # Description with comma is still string


if __name__ == "__main__":
    unittest.main()
