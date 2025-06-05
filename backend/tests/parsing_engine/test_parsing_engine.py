# backend/tests/parsing_engine/test_parsing_engine.py

import unittest
import json

# Assuming tests run from 'backend' directory or using a test runner that handles PYTHONPATH
from app.core.parsing_engine import ParsingEngine
from app.core.parsing_engine.intermediate_schema import SchemaISR, TableISR, ColumnISR, ConstraintDetail

class TestParsingEngineIntegration(unittest.TestCase): # Renamed for broader scope

    def setUp(self):
        self.engine = ParsingEngine()
        # Define a more comprehensive sample JSON for reuse
        self.sample_json_data = {
            "schema_name": "MusicDB_v2",
            "version": "2.0",
            "tables": [
                {
                    "name": "artists",
                    "comment": "Stores artist information",
                    "columns": [
                        {"name": "id", "generic_type": "INTEGER", "constraints": [{"type": "PRIMARY_KEY"}, {"type": "AUTO_INCREMENT"}], "comment": "Artist ID"},
                        {"name": "name", "generic_type": "STRING", "constraints": [{"type": "NOT_NULL"}, {"type": "UNIQUE"}], "comment": "Artist's full name"}
                    ]
                },
                {
                    "name": "albums",
                    "comment": "Stores album information",
                    "columns": [
                        {"name": "album_id", "generic_type": "INTEGER", "constraints": [{"type": "PRIMARY_KEY"}, {"type": "AUTO_INCREMENT"}]},
                        {"name": "title", "generic_type": "STRING", "constraints": [{"type": "NOT_NULL"}]},
                        {"name": "artist_id", "generic_type": "INTEGER",
                         "constraints": [
                             {"type": "FOREIGN_KEY", "details": {"references_table": "artists", "references_columns": ["id"], "name": "fk_album_artist", "on_delete": "CASCADE"}}
                         ]
                        },
                        {"name": "release_year", "generic_type": "INTEGER", "constraints": [{"type": "NOT_NULL"}]},
                        {"name": "genre", "generic_type": "ENUM_TYPE",
                         "constraints": [
                             {"type": "ENUM_VALUES", "details": {"values": ["Rock", "Pop", "Jazz", "Classical", "Electronic"]}},
                             {"type": "DEFAULT", "details":{"value": "Rock"}}
                         ]
                        }
                    ]
                }
            ]
        }
        self.sample_json_string = json.dumps(self.sample_json_data)

    def test_generate_schema_with_valid_json(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_json_string, "json")
        self.assertIsInstance(schema_isr, SchemaISR)
        self.assertEqual(schema_isr.schema_name, "MusicDB_v2")
        self.assertEqual(schema_isr.version, "2.0")
        self.assertEqual(len(schema_isr.tables), 2)

        artists_table = next(t for t in schema_isr.tables if t.name == "artists")
        self.assertIsNotNone(artists_table)
        self.assertEqual(artists_table.comment, "Stores artist information")
        self.assertEqual(len(artists_table.columns), 2)

        albums_table = next(t for t in schema_isr.tables if t.name == "albums")
        self.assertIsNotNone(albums_table)
        self.assertEqual(len(albums_table.columns), 5)

    def test_generate_schema_with_invalid_json_structure(self):
        # Example: 'tables' key is misspelled
        invalid_json_string = json.dumps({"schema_name": "Test", "tablez": []})
        with self.assertRaisesRegex(ValueError, "Missing or invalid 'tables' list"):
            self.engine.generate_schema_from_input(invalid_json_string, "json")

    def test_generate_schema_with_malformed_json_string(self):
        malformed_json_string = '{"schema_name": "Test", "tables": [}' # Malformed JSON
        with self.assertRaisesRegex(ValueError, "Invalid JSON format"):
            self.engine.generate_schema_from_input(malformed_json_string, "json")

    def test_generate_schema_with_unsupported_type(self):
        with self.assertRaisesRegex(NotImplementedError, "Parser for input type 'xml' is not implemented."):
            self.engine.generate_schema_from_input("<data></data>", "xml")

    def test_convert_isr_to_mysql_ddl_integration(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_json_string, "json")
        self.assertIsNotNone(schema_isr)

        mysql_ddl = self.engine.convert_isr_to_target_ddl(schema_isr, "mysql")

        # General DDL structure checks
        self.assertIn("-- Schema: MusicDB_v2", mysql_ddl)
        self.assertIn("-- Version: 2.0", mysql_ddl)
        self.assertIn("SET FOREIGN_KEY_CHECKS=0;", mysql_ddl)
        self.assertIn("SET FOREIGN_KEY_CHECKS=1;", mysql_ddl)

        # Artists table checks
        self.assertIn("DROP TABLE IF EXISTS `artists`;", mysql_ddl)
        self.assertIn("CREATE TABLE `artists` (", mysql_ddl)
        self.assertIn("`id` INT AUTO_INCREMENT COMMENT 'Artist ID'", mysql_ddl)
        self.assertIn("`name` VARCHAR(255) NOT NULL UNIQUE COMMENT 'Artist''s full name'", mysql_ddl) # Escaped quote
        self.assertIn("PRIMARY KEY (`id`)", mysql_ddl)
        self.assertIn(") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Stores artist information';", mysql_ddl)

        # Albums table checks
        self.assertIn("DROP TABLE IF EXISTS `albums`;", mysql_ddl)
        self.assertIn("CREATE TABLE `albums` (", mysql_ddl)
        self.assertIn("`album_id` INT AUTO_INCREMENT", mysql_ddl)
        self.assertIn("`title` VARCHAR(255) NOT NULL", mysql_ddl)
        self.assertIn("`artist_id` INT", mysql_ddl) # FK column
        self.assertIn("`release_year` INT NOT NULL", mysql_ddl)
        self.assertIn("`genre` ENUM('Rock', 'Pop', 'Jazz', 'Classical', 'Electronic') DEFAULT 'Rock'", mysql_ddl)
        self.assertIn("PRIMARY KEY (`album_id`)", mysql_ddl)
        self.assertIn(") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Stores album information';", mysql_ddl)

        # Foreign Key check
        self.assertIn("ALTER TABLE `albums` ADD CONSTRAINT `fk_album_artist` FOREIGN KEY (`artist_id`) REFERENCES `artists` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION;", mysql_ddl)

    def test_convert_isr_to_unsupported_ddl_target(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_json_string, "json")
        with self.assertRaisesRegex(NotImplementedError, "Adapter for target database 'postgresql' is not implemented."):
            self.engine.convert_isr_to_target_ddl(schema_isr, "postgresql")

if __name__ == "__main__":
    unittest.main()
