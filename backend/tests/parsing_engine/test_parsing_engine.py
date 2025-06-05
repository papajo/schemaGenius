# backend/tests/parsing_engine/test_parsing_engine.py

import unittest
import json

from app.core.parsing_engine import ParsingEngine
from app.core.parsing_engine.intermediate_schema import SchemaISR, TableISR, ColumnISR, ConstraintDetail

class TestParsingEngineIntegration(unittest.TestCase):

    def setUp(self):
        self.engine = ParsingEngine()
        self.sample_json_string = json.dumps({
            "schema_name": "MusicDB_JSON",
            "tables": [{
                "name": "albums",
                "columns": [
                    {"name": "id", "generic_type": "INTEGER", "constraints": [{"type": "PRIMARY_KEY"}]},
                    {"name": "title", "generic_type": "STRING", "constraints": [{"type": "NOT_NULL"}]}
                ]
            }]
        })
        self.sample_sql_ddl = """
        CREATE TABLE `artists` (
            `artist_id` INT PRIMARY KEY AUTO_INCREMENT,
            `name` VARCHAR(255) NOT NULL
        );
        """
        self.sample_csv_data = "header_A,header_B,header_C\ntext_val,100,true\nother_val,200,false\nlast_val,300,T"

    # --- JSON Input Tests ---
    def test_generate_schema_with_valid_json(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_json_string, "json")
        self.assertIsInstance(schema_isr, SchemaISR)
        self.assertEqual(schema_isr.schema_name, "MusicDB_JSON")
        self.assertEqual(len(schema_isr.tables), 1)
        self.assertEqual(schema_isr.tables[0].name, "albums")

    # --- SQL Input Tests ---
    def test_generate_schema_with_valid_sql(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_sql_ddl, "sql")
        self.assertIsInstance(schema_isr, SchemaISR)
        self.assertEqual(len(schema_isr.tables), 1)
        self.assertEqual(schema_isr.tables[0].name, "artists")
        # Add more assertions based on the expected output of your SQL parser stub
        self.assertEqual(len(schema_isr.tables[0].columns), 2)


    # --- CSV Input Tests (New) ---
    def test_generate_schema_with_valid_csv(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_csv_data, "csv", source_name="my_csv_table_data")
        self.assertIsInstance(schema_isr, SchemaISR)
        self.assertEqual(len(schema_isr.tables), 1)
        table = schema_isr.tables[0]
        self.assertEqual(table.name, "my_csv_table_data") # Name from source_name, cleaned by parser
        self.assertEqual(len(table.columns), 3)

        # Check column names and inferred types
        expected_cols = {"header_A": "STRING", "header_B": "INTEGER", "header_C": "BOOLEAN"}
        for col in table.columns:
            self.assertIn(col.name, expected_cols.keys())
            self.assertEqual(col.generic_type, expected_cols[col.name])

    def test_generate_schema_with_empty_csv(self):
        schema_isr = self.engine.generate_schema_from_input("", "csv", source_name="empty_csv_data")
        self.assertEqual(len(schema_isr.tables), 0)

    def test_generate_schema_with_csv_header_only(self):
        header_only_csv = "col1,col2,col3"
        schema_isr = self.engine.generate_schema_from_input(header_only_csv, "csv", source_name="header_only_csv_data")
        self.assertEqual(len(schema_isr.tables), 1)
        table = schema_isr.tables[0]
        self.assertEqual(table.name, "header_only_csv_data")
        self.assertEqual(len(table.columns), 3)
        self.assertTrue(all(c.generic_type == "STRING" for c in table.columns))


    # --- Error Handling and DDL Conversion Tests (common) ---
    def test_generate_schema_with_unsupported_input_type(self):
        with self.assertRaisesRegex(NotImplementedError, "Parser for input type 'xml' is not implemented."):
            self.engine.generate_schema_from_input("data", "xml")

    def test_convert_isr_from_json_to_mysql_ddl(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_json_string, "json")
        mysql_ddl = self.engine.convert_isr_to_target_ddl(schema_isr, "mysql")
        self.assertIn("CREATE TABLE `albums`", mysql_ddl)
        self.assertIn("`title` VARCHAR(255) NOT NULL", mysql_ddl)

    def test_convert_isr_from_sql_to_mysql_ddl(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_sql_ddl, "sql")
        mysql_ddl = self.engine.convert_isr_to_target_ddl(schema_isr, "mysql")
        self.assertIn("CREATE TABLE `artists`", mysql_ddl)
        self.assertIn("`name` VARCHAR(255) NOT NULL", mysql_ddl) # Based on current SQL parser stub

    def test_convert_isr_from_csv_to_mysql_ddl(self):
        # source_name is important for CSV table naming
        schema_isr = self.engine.generate_schema_from_input(self.sample_csv_data, "csv", source_name="from_csv_data")
        mysql_ddl = self.engine.convert_isr_to_target_ddl(schema_isr, "mysql")
        self.assertIn("CREATE TABLE `from_csv_data`", mysql_ddl)
        self.assertIn("`header_A` VARCHAR(255)", mysql_ddl) # Inferred as STRING
        self.assertIn("`header_B` INT", mysql_ddl)         # Inferred as INTEGER
        self.assertIn("`header_C` BOOLEAN", mysql_ddl)     # Inferred as BOOLEAN

    def test_convert_isr_to_unsupported_ddl_target(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_json_string, "json")
        with self.assertRaisesRegex(NotImplementedError, "Adapter for target database 'oracle' is not implemented."):
            self.engine.convert_isr_to_target_ddl(schema_isr, "oracle")

if __name__ == "__main__":
    unittest.main()
