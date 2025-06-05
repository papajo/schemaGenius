# backend/tests/parsing_engine/test_parsing_engine.py

import unittest
import json

from app.core.parsing_engine import ParsingEngine
from app.core.parsing_engine.intermediate_schema import SchemaISR, TableISR, ColumnISR, ConstraintDetail
from typing import Optional # For Mapped[Optional[str]] in sample code

class TestParsingEngineIntegration(unittest.TestCase):

    def setUp(self):
        self.engine = ParsingEngine()
        # Simplified JSON for basic checks, detailed JSON tests are in test_json_parser.py
        self.sample_json_string = json.dumps({
            "schema_name": "JsonDb",
            "tables": [{"name": "json_table", "columns": [{"name": "data_col", "generic_type": "TEXT"}]}]
        })
        # Simplified SQL for basic checks, detailed SQL tests are in test_sql_parser.py
        self.sample_sql_ddl = """
        CREATE TABLE sql_table_1 (id INT PRIMARY KEY, description TEXT);
        CREATE TABLE sql_table_2 (ref_id INT, notes VARCHAR(100));
        """
        # Simplified CSV for basic checks, detailed CSV tests are in test_csv_parser.py
        self.sample_csv_data = "csv_col_id,csv_col_name,csv_col_active\n1,ItemA,true\n2,ItemB,false"

        # More comprehensive Python ORM code for testing this specific integration
        self.sample_python_orm_code = """
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, Float, Numeric, Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from typing import Optional # Required for Mapped[Optional[str]]
import datetime

Base = declarative_base()

class OrmUser(Base):
    __tablename__ = "orm_users_table"
    '''User table comment from docstring.'''

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="Primary ID for users")
    username: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(120), unique=True) # Nullable due to Optional
    is_verified: Mapped[bool] = mapped_column(default=False)

class OrmPost(Base):
    __tablename__ = "orm_posts_table"

    post_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="Post primary key") # Using Integer directly
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    content = Column(Text) # Using traditional Column
    author_id: Mapped[int] = mapped_column(ForeignKey("orm_users_table.user_id"), comment="Link to author")
    status = Column(SQLAlchemyEnum("draft", "published", name="post_status_enum"), default="draft")
"""

    # --- JSON Input Tests ---
    def test_generate_schema_with_valid_json(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_json_string, "json")
        self.assertIsInstance(schema_isr, SchemaISR)
        self.assertEqual(schema_isr.schema_name, "JsonDb")
        self.assertEqual(len(schema_isr.tables), 1)
        self.assertEqual(schema_isr.tables[0].name, "json_table")

    # --- SQL Input Tests ---
    def test_generate_schema_with_valid_sql(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_sql_ddl, "sql")
        self.assertIsInstance(schema_isr, SchemaISR)
        self.assertEqual(len(schema_isr.tables), 2) # sql_table_1, sql_table_2
        self.assertTrue(any(t.name == "sql_table_1" for t in schema_isr.tables))
        self.assertTrue(any(t.name == "sql_table_2" for t in schema_isr.tables))

    # --- CSV Input Tests ---
    def test_generate_schema_with_valid_csv(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_csv_data, "csv", source_name="my_csv_table")
        self.assertIsInstance(schema_isr, SchemaISR)
        self.assertEqual(len(schema_isr.tables), 1)
        table = schema_isr.tables[0]
        self.assertEqual(table.name, "my_csv_table")
        self.assertEqual(len(table.columns), 3)
        self.assertEqual(table.columns[1].name, "csv_col_name")
        self.assertEqual(table.columns[1].generic_type, "STRING")
        self.assertEqual(table.columns[2].generic_type, "BOOLEAN")

    # --- Python ORM Input Tests (New/Enhanced) ---
    def test_generate_schema_with_valid_python_orm(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_python_orm_code, "python")
        self.assertIsInstance(schema_isr, SchemaISR)
        self.assertEqual(len(schema_isr.tables), 2, "Should parse OrmUser and OrmPost tables")

        user_table = next((t for t in schema_isr.tables if t.name == "orm_users_table"), None)
        self.assertIsNotNone(user_table)
        self.assertEqual(user_table.comment.strip(), "User table comment from docstring.")
        self.assertEqual(len(user_table.columns), 4) # user_id, username, email, is_verified

        user_id_col = next(c for c in user_table.columns if c.name == "user_id")
        self.assertEqual(user_id_col.comment, "Primary ID for users")
        self.assertTrue(any(con.type == "PRIMARY_KEY" for con in user_id_col.constraints))
        self.assertTrue(any(con.type == "AUTO_INCREMENT" for con in user_id_col.constraints))

        email_col = next(c for c in user_table.columns if c.name == "email")
        self.assertFalse(any(con.type == "NOT_NULL" for con in email_col.constraints)) # Mapped[Optional[str]]

        post_table = next((t for t in schema_isr.tables if t.name == "orm_posts_table"), None)
        self.assertIsNotNone(post_table)
        self.assertEqual(len(post_table.columns), 5) # post_id, title, content, author_id, status

        author_id_col = next(c for c in post_table.columns if c.name == "author_id")
        fk_constraint = next((con for con in author_id_col.constraints if con.type == "FOREIGN_KEY"), None)
        self.assertIsNotNone(fk_constraint)
        self.assertEqual(fk_constraint.details.get("references_table"), "orm_users_table")
        self.assertEqual(fk_constraint.details.get("references_column"), "user_id")
        self.assertEqual(author_id_col.comment, "Link to author")

        status_col = next(c for c in post_table.columns if c.name == "status")
        self.assertEqual(status_col.generic_type, "ENUM_TYPE")
        enum_vals_constr = next(c for c in status_col.constraints if c.type == "ENUM_VALUES")
        self.assertEqual(enum_vals_constr.details.get("values"), ["draft", "published", "archived"])


    # --- End-to-End Conversion Tests (Including Python ORM to DDL) ---
    def test_convert_isr_from_python_orm_to_mysql_ddl(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_python_orm_code, "sqlalchemy") # Test alias
        mysql_ddl = self.engine.convert_isr_to_target_ddl(schema_isr, "mysql")

        self.assertIn("CREATE TABLE `orm_users_table`", mysql_ddl)
        self.assertIn("`user_id` INT AUTO_INCREMENT COMMENT 'Primary ID for users'", mysql_ddl)
        self.assertIn("`email` VARCHAR(255) UNIQUE", mysql_ddl) # String(120) -> VARCHAR(255) by current map
        self.assertIn("COMMENT ON TABLE `orm_users_table` IS 'User table comment from docstring.'", mysql_ddl) # Check table comment

        self.assertIn("CREATE TABLE `orm_posts_table`", mysql_ddl)
        self.assertIn("`status` ENUM('draft', 'published', 'archived') DEFAULT 'draft'", mysql_ddl)
        self.assertIn("FOREIGN KEY (`author_id`) REFERENCES `orm_users_table` (`user_id`)", mysql_ddl)

    def test_convert_isr_from_python_orm_to_postgresql_ddl(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_python_orm_code, "python")
        pg_ddl = self.engine.convert_isr_to_target_ddl(schema_isr, "postgresql")

        self.assertIn('CREATE TYPE "enum_orm_posts_table_status" AS ENUM (\'draft\', \'published\', \'archived\');', pg_ddl)
        self.assertIn('CREATE TABLE "orm_users_table" (', pg_ddl)
        self.assertIn('    "user_id" SERIAL', pg_ddl)
        self.assertIn('COMMENT ON COLUMN "orm_users_table"."user_id" IS \'Primary ID for users\';', pg_ddl)
        self.assertIn('COMMENT ON TABLE "orm_users_table" IS \'User table comment from docstring.\';', pg_ddl)

        self.assertIn('CREATE TABLE "orm_posts_table" (', pg_ddl)
        self.assertIn('    "status" "enum_orm_posts_table_status" DEFAULT \'draft\'', pg_ddl)
        self.assertIn('ALTER TABLE "orm_posts_table" ADD CONSTRAINT "fk_orm_posts_table_author_id" FOREIGN KEY ("author_id") REFERENCES "orm_users_table" ("user_id");', pg_ddl)


    # --- General Error Handling Tests ---
    def test_generate_schema_with_unsupported_input_type(self):
        with self.assertRaisesRegex(NotImplementedError, "Parser for input type 'textile' is not implemented."):
            self.engine.generate_schema_from_input("data", "textile") # Changed from 'text' to a clearly unsupported one for this test

    def test_convert_isr_to_unsupported_ddl_target(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_json_string, "json")
        with self.assertRaisesRegex(NotImplementedError, "Adapter for target database 'db2' is not implemented."):
            self.engine.convert_isr_to_target_ddl(schema_isr, "db2")


if __name__ == "__main__":
    unittest.main()
