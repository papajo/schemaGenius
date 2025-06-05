# backend/tests/parsing_engine/parsers/test_json_parser.py

import unittest
import json # For crafting test inputs

from app.core.parsing_engine.parsers.json_parser import parse_json_input
from app.core.parsing_engine.intermediate_schema import SchemaISR, TableISR, ColumnISR, ConstraintDetail

class TestJsonParser(unittest.TestCase):

    def test_parse_valid_simple_json(self):
        json_input = {
            "schema_name": "TestDB",
            "version": "1.1",
            "tables": [
                {
                    "name": "users",
                    "comment": "User table",
                    "columns": [
                        {"name": "id", "generic_type": "INTEGER", "comment": "Primary key", "constraints": [{"type": "PRIMARY_KEY"}]},
                        {"name": "email", "generic_type": "STRING", "constraints": [{"type": "UNIQUE"}, {"type": "NOT_NULL"}]}
                    ]
                }
            ]
        }
        json_string = json.dumps(json_input)
        schema_isr = parse_json_input(json_string)
        self.assertIsInstance(schema_isr, SchemaISR)
        self.assertEqual(schema_isr.schema_name, "TestDB")
        self.assertEqual(schema_isr.version, "1.1")
        self.assertEqual(len(schema_isr.tables), 1)
        table1 = schema_isr.tables[0]
        self.assertEqual(table1.name, "users")
        self.assertEqual(table1.comment, "User table")
        self.assertEqual(len(table1.columns), 2)
        col1 = table1.columns[0]
        self.assertEqual(col1.name, "id")
        self.assertEqual(col1.generic_type, "INTEGER")
        self.assertEqual(col1.comment, "Primary key")
        self.assertEqual(len(col1.constraints), 1)
        self.assertEqual(col1.constraints[0].type, "PRIMARY_KEY")
        col2 = table1.columns[1]
        self.assertEqual(len(col2.constraints), 2)
        self.assertEqual(col2.constraints[0].type, "UNIQUE")
        self.assertEqual(col2.constraints[1].type, "NOT_NULL")

    def test_parse_malformed_json(self):
        json_string = "{\\"tables\\": [{\\"name\\": \\"users\\"}" # Missing closing brace and quote, escaped for bash
        with self.assertRaisesRegex(ValueError, "Invalid JSON format"):
            parse_json_input(json_string)

    def test_missing_tables_key(self):
        json_string = json.dumps({"schema_name": "NoTablesDB"})
        with self.assertRaisesRegex(ValueError, "Missing or invalid .*tables.* list"):
            parse_json_input(json_string)

    def test_missing_table_name(self):
        json_string = json.dumps({"tables": [{"columns": [{"name": "id", "generic_type": "INTEGER"}]}]})
        with self.assertRaisesRegex(ValueError, "Missing .*name.* for table"):
            parse_json_input(json_string)

    def test_missing_column_name_or_type(self):
        json_string = json.dumps({"tables": [{"name": "users", "columns": [{"generic_type": "INTEGER"}]}]})
        with self.assertRaisesRegex(ValueError, "Missing .*name.* or .*generic_type.* for column"):
            parse_json_input(json_string)

    def test_invalid_constraints_format(self):
        json_string = json.dumps({"tables": [{"name": "users", "columns": [{"name": "id", "generic_type": "INTEGER", "constraints": ["PRIMARY_KEY"]}]}]}) # Constraint should be dict
        with self.assertRaisesRegex(ValueError, "Invalid constraint format"):
            parse_json_input(json_string)

if __name__ == "__main__":
    unittest.main()
