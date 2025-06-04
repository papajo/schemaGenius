# backend/tests/parsing_engine/test_parsing_engine.py

import unittest
import json

from app.core.parsing_engine import ParsingEngine
from app.core.parsing_engine.intermediate_schema import SchemaISR

class TestParsingEngineJsonIntegration(unittest.TestCase):

    def setUp(self):
        self.engine = ParsingEngine()

    def test_generate_schema_with_valid_json(self):
        valid_json_data = {
            "schema_name": "MusicDB",
            "tables": [
                {
                    "name": "artists",
                    "columns": [
                        {"name": "id", "generic_type": "INTEGER", "constraints": [{"type": "PRIMARY_KEY"}]}
                    ]
                }
            ]
        }
        valid_json_string = json.dumps(valid_json_data)
        schema_isr = self.engine.generate_schema_from_input(valid_json_string, "json")
        self.assertIsInstance(schema_isr, SchemaISR)
        self.assertEqual(schema_isr.schema_name, "MusicDB")
        self.assertEqual(len(schema_isr.tables), 1)
        self.assertEqual(schema_isr.tables[0].name, "artists")

    def test_generate_schema_with_invalid_json_structure(self):
        invalid_json_data = {"schema_name": "BrokenDB", "tablez": []}
        invalid_json_string = json.dumps(invalid_json_data)
        with self.assertRaisesRegex(ValueError, "Missing or invalid .*tables.* list"):
            self.engine.generate_schema_from_input(invalid_json_string, "json")

    def test_generate_schema_with_malformed_json_string(self):
        malformed_json_string = "{\\"schema_name\\": \\"Malformed\\"" # Escaped for bash
        with self.assertRaisesRegex(ValueError, "Invalid JSON format"):
            self.engine.generate_schema_from_input(malformed_json_string, "json")

    def test_generate_schema_with_unsupported_type(self):
        with self.assertRaises(NotImplementedError):
            self.engine.generate_schema_from_input("some data", "xml")

    def test_convert_isr_to_target_ddl_placeholder(self):
        dummy_isr = SchemaISR(tables=[])
        ddl_output = self.engine.convert_isr_to_target_ddl(dummy_isr, "mysql")
        self.assertIn("-- Placeholder DDL for mysql", ddl_output)

if __name__ == "__main__":
    unittest.main()
