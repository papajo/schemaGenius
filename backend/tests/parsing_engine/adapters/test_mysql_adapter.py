# backend/tests/parsing_engine/adapters/test_mysql_adapter.py

import unittest
from app.core.parsing_engine.intermediate_schema import SchemaISR, TableISR, ColumnISR, ConstraintDetail
from app.core.parsing_engine.adapters.mysql_adapter import convert_isr_to_mysql_ddl, _map_generic_type_to_mysql

class TestMySQLAdapter(unittest.TestCase):

    def test_map_generic_type_to_mysql(self):
        self.assertEqual(_map_generic_type_to_mysql("STRING", []), "VARCHAR(255)")
        self.assertEqual(_map_generic_type_to_mysql("INTEGER", []), "INT")
        self.assertEqual(_map_generic_type_to_mysql("BOOLEAN", []), "BOOLEAN")

        # Test ENUM
        enum_constraint = ConstraintDetail({"type": "ENUM_VALUES", "values": ["A", "B", "C'est la vie"]})
        # Expected: ENUM('A', 'B', 'C''est la vie') - single quotes inside are doubled
        expected_enum_ddl = "ENUM('A', 'B', 'C''est la vie')" # Quotes inside SQL string are escaped by doubling
        self.assertEqual(_map_generic_type_to_mysql("ENUM_TYPE", [enum_constraint]), expected_enum_ddl)

        # Test ENUM fallback
        self.assertEqual(_map_generic_type_to_mysql("ENUM_TYPE", []), "VARCHAR(255)")

        # Test TIMESTAMP (default was removed from map, handled by DEFAULT constraint)
        self.assertEqual(_map_generic_type_to_mysql("TIMESTAMP", []), "TIMESTAMP")

        self.assertEqual(_map_generic_type_to_mysql("UNKNOWN_TYPE", []), "VARCHAR(255)") # Test fallback

    def test_simple_table_creation(self):
        col1 = ColumnISR(name="id", generic_type="INTEGER",
                         constraints=[ConstraintDetail({"type": "PRIMARY_KEY"}),
                                      ConstraintDetail({"type": "AUTO_INCREMENT"})],
                         comment="User ID")
        col2 = ColumnISR(name="username", generic_type="STRING",
                         constraints=[ConstraintDetail({"type": "NOT_NULL"}),
                                      ConstraintDetail({"type": "UNIQUE"})],
                         comment="Unique username")
        table1 = TableISR(name="users", columns=[col1, col2], comment="System users table")
        schema_isr = SchemaISR(tables=[table1], schema_name="MyTestDB", version="1.0")

        ddl = convert_isr_to_mysql_ddl(schema_isr)

        self.assertIn("-- Schema: MyTestDB", ddl)
        self.assertIn("-- Version: 1.0", ddl)
        self.assertIn("DROP TABLE IF EXISTS `users`;", ddl)

        # Normalize expected DDL for robust comparison (order of lines, spacing)
        # This is a simplified check; more rigorous parsing or regex might be needed for complex cases.
        expected_parts = [
            "CREATE TABLE `users` (",
            "`id` INT AUTO_INCREMENT COMMENT 'User ID'",
            "`username` VARCHAR(255) NOT NULL UNIQUE COMMENT 'Unique username'",
            "PRIMARY KEY (`id`)",
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='System users table';"
        ]
        for part in expected_parts:
            self.assertIn(part, ddl)

    def test_foreign_key_generation(self):
        # users table
        user_id_col = ColumnISR(name="id", generic_type="INTEGER", constraints=[ConstraintDetail({"type": "PRIMARY_KEY"})])
        users_table = TableISR(name="users", columns=[user_id_col])

        # posts table
        post_id_col = ColumnISR(name="post_id", generic_type="INTEGER", constraints=[ConstraintDetail({"type": "PRIMARY_KEY"})])
        fk_details = {
            "references_table": "users",
            "references_columns": ["id"], # Now a list as per intermediate_schema
            "on_delete": "CASCADE",
            "name": "fk_post_author" # Optional name for the FK constraint
        }
        user_fk_col = ColumnISR(name="author_id", generic_type="INTEGER",
                                constraints=[ConstraintDetail({"type": "FOREIGN_KEY", "details": fk_details})])
        posts_table = TableISR(name="posts", columns=[post_id_col, user_fk_col])

        schema_isr = SchemaISR(tables=[users_table, posts_table])
        ddl = convert_isr_to_mysql_ddl(schema_isr)

        expected_fk_statement = "ALTER TABLE `posts` ADD CONSTRAINT `fk_post_author` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION;"
        self.assertIn(expected_fk_statement, ddl)

    def test_default_value_handling(self):
        col_ts = ColumnISR(name="created_at", generic_type="TIMESTAMP",
                           constraints=[ConstraintDetail({"type": "DEFAULT", "value": "CURRENT_TIMESTAMP"})])
        col_status = ColumnISR(name="status", generic_type="STRING",
                               constraints=[ConstraintDetail({"type": "DEFAULT", "value": "pending"})])
        col_active = ColumnISR(name="is_active", generic_type="BOOLEAN",
                               constraints=[ConstraintDetail({"type": "DEFAULT", "value": True})])

        table = TableISR(name="jobs", columns=[col_ts, col_status, col_active])
        schema_isr = SchemaISR(tables=[table])
        ddl = convert_isr_to_mysql_ddl(schema_isr)

        self.assertIn("`created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP", ddl)
        self.assertIn("`status` VARCHAR(255) DEFAULT 'pending'", ddl)
        self.assertIn("`is_active` BOOLEAN DEFAULT TRUE", ddl)

    def test_enum_type_generation(self):
        enum_constraint = ConstraintDetail({"type": "ENUM_VALUES", "values": ["pending", "processing", "completed", "failed"]})
        col_enum = ColumnISR(name="job_status", generic_type="ENUM_TYPE", constraints=[enum_constraint])
        table = TableISR(name="tasks", columns=[col_enum])
        schema_isr = SchemaISR(tables=[table])
        ddl = convert_isr_to_mysql_ddl(schema_isr)

        self.assertIn("`job_status` ENUM('pending', 'processing', 'completed', 'failed')", ddl)

if __name__ == "__main__":
    unittest.main()
