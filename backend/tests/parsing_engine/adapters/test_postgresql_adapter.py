# backend/tests/parsing_engine/adapters/test_postgresql_adapter.py

import unittest
# Assuming tests are run from 'backend' directory or test runner handles paths
from app.core.parsing_engine.intermediate_schema import SchemaISR, TableISR, ColumnISR, ConstraintDetail
from app.core.parsing_engine.adapters.postgresql_adapter import convert_isr_to_postgresql_ddl, _map_generic_type_to_postgresql, _get_column_constraints_ddl, _clean_identifier

class TestPostgreSQLAdapter(unittest.TestCase):

    def test_map_generic_type_to_postgresql(self):
        # Basic types
        # The _map_generic_type_to_postgresql expects a ColumnISR object.
        # The second argument `custom_enum_types` is a set of strings, usually empty for non-enum tests.
        self.assertEqual(_map_generic_type_to_postgresql(ColumnISR(name="c", generic_type="STRING", constraints=[]), set()), "VARCHAR(255)")
        self.assertEqual(_map_generic_type_to_postgresql(ColumnISR(name="c", generic_type="INTEGER", constraints=[]), set()), "INTEGER")
        self.assertEqual(_map_generic_type_to_postgresql(ColumnISR(name="c", generic_type="DATETIME", constraints=[]), set()), "TIMESTAMP WITHOUT TIME ZONE")
        self.assertEqual(_map_generic_type_to_postgresql(ColumnISR(name="c", generic_type="TIMESTAMP", constraints=[]), set()), "TIMESTAMP WITH TIME ZONE")
        self.assertEqual(_map_generic_type_to_postgresql(ColumnISR(name="c", generic_type="JSON_TYPE", constraints=[]), set()), "JSONB")

        # SERIAL types
        pk_auto_int_constraints = [ConstraintDetail({"type": "PRIMARY_KEY"}), ConstraintDetail({"type": "AUTO_INCREMENT"})]
        pk_auto_int = ColumnISR(name="id", generic_type="INTEGER", constraints=pk_auto_int_constraints)
        self.assertEqual(_map_generic_type_to_postgresql(pk_auto_int, set()), "SERIAL")

        pk_auto_bigint_constraints = [ConstraintDetail({"type": "PRIMARY_KEY"}), ConstraintDetail({"type": "AUTO_INCREMENT"})]
        pk_auto_bigint = ColumnISR(name="id", generic_type="BIG_INTEGER", constraints=pk_auto_bigint_constraints)
        self.assertEqual(_map_generic_type_to_postgresql(pk_auto_bigint, set()), "BIGSERIAL")

        # ENUM placeholder - this test reflects the current stub behavior of _map_generic_type_to_postgresql
        enum_col_constraints = [ConstraintDetail({"type": "ENUM_VALUES", "details": {"values": ["active", "pending"]}})]
        enum_col = ColumnISR(name="status", generic_type="ENUM_TYPE", constraints=enum_col_constraints)
        # The _map_generic_type_to_postgresql itself returns a placeholder string for ENUMs;
        # the main convert_isr_to_postgresql_ddl function replaces this with the actual generated enum type name.
        self.assertIn("TEXT /* ENUM: status", _map_generic_type_to_postgresql(enum_col, set()))


    def test_simple_table_ddl_generation(self):
        pk_col = ColumnISR(name="id", generic_type="INTEGER", constraints=[ConstraintDetail({"type": "PRIMARY_KEY"}), ConstraintDetail({"type": "AUTO_INCREMENT"})])
        name_col = ColumnISR(name="name", generic_type="STRING", constraints=[ConstraintDetail({"type": "NOT_NULL"}), ConstraintDetail({"type": "UNIQUE"})], comment="User's full name")
        users_table = TableISR(name="app users", columns=[pk_col, name_col], comment="Stores application users") # Intentionally with space
        schema = SchemaISR(tables=[users_table], schema_name="MyDatabase", version="1.0")

        ddl = convert_isr_to_postgresql_ddl(schema)
        # print(f"\nSimple Table DDL (PostgreSQL):\n{ddl}") # For debugging

        self.assertIn("-- Schema: MyDatabase", ddl)
        self.assertIn("-- Version: 1.0", ddl)
        self.assertIn('CREATE TABLE "app_users" (', ddl) # Check cleaned and quoted table name
        self.assertIn('    "id" SERIAL', ddl)
        self.assertIn('    "name" VARCHAR(255) NOT NULL UNIQUE', ddl)
        self.assertIn(');', ddl)
        self.assertIn('COMMENT ON TABLE "app_users" IS \'Stores application users\';', ddl)
        self.assertIn('COMMENT ON COLUMN "app_users"."name" IS \'User\'\'s full name\';', ddl)


    def test_enum_type_and_foreign_key_ddl_generation(self):
        author_pk = ColumnISR(name="author_id", generic_type="INTEGER", constraints=[ConstraintDetail({"type":"PRIMARY_KEY"}), ConstraintDetail({"type":"AUTO_INCREMENT"})])
        author_name_col = ColumnISR(name="author_name", generic_type="STRING", constraints=[ConstraintDetail({"type":"NOT_NULL"})])
        authors_table = TableISR(name="authors", columns=[author_pk, author_name_col])

        book_pk = ColumnISR(name="book_id", generic_type="INTEGER", constraints=[ConstraintDetail({"type":"PRIMARY_KEY"}), ConstraintDetail({"type":"AUTO_INCREMENT"})])
        book_title_col = ColumnISR(name="title", generic_type="TEXT", constraints=[ConstraintDetail({"type":"NOT_NULL"})])

        book_status_constraints = [
            ConstraintDetail({"type": "ENUM_VALUES", "details": {"values": ["published", "draft", "out of print"]}}), # Value with space
            ConstraintDetail({"type": "DEFAULT", "details": {"value": "draft"}})
        ]
        book_status_col = ColumnISR(name="status", generic_type="ENUM_TYPE", constraints=book_status_constraints)

        fk_author_details = {
            "name": "fk_book_author",
            "references_table": "authors",
            "references_columns": ["author_id"],
            "on_delete": "SET NULL"
        }
        book_author_fk_col = ColumnISR(name="author_id_fk", generic_type="INTEGER", constraints=[ConstraintDetail({"type": "FOREIGN_KEY", "details": fk_author_details})])

        books_table = TableISR(name="books", columns=[book_pk, book_title_col, book_status_col, book_author_fk_col])
        schema = SchemaISR(tables=[authors_table, books_table])

        ddl = convert_isr_to_postgresql_ddl(schema)
        # print(f"\nEnum & FK Table DDL (PostgreSQL):\n{ddl}")

        self.assertIn('CREATE TYPE "enum_books_status" AS ENUM (\'published\', \'draft\', \'out of print\');', ddl)

        self.assertIn('CREATE TABLE "authors" (', ddl)
        self.assertIn('    "author_id" SERIAL', ddl)
        self.assertIn('    "author_name" VARCHAR(255) NOT NULL', ddl)

        self.assertIn('CREATE TABLE "books" (', ddl)
        self.assertIn('    "book_id" SERIAL', ddl)
        self.assertIn('    "title" TEXT NOT NULL', ddl)
        self.assertIn('    "status" "enum_books_status" DEFAULT \'draft\'', ddl)
        self.assertIn('    "author_id_fk" INTEGER', ddl)

        self.assertIn('ALTER TABLE "books" ADD CONSTRAINT "fk_book_author" FOREIGN KEY ("author_id_fk") REFERENCES "authors" ("author_id") ON DELETE SET NULL;', ddl)

    def test_composite_primary_key(self):
        col1 = ColumnISR(name="order_id", generic_type="INTEGER", constraints=[ConstraintDetail({"type": "PRIMARY_KEY"})])
        col2 = ColumnISR(name="product_id", generic_type="INTEGER", constraints=[ConstraintDetail({"type": "PRIMARY_KEY"})])
        col_qty = ColumnISR(name="quantity", generic_type="INTEGER", constraints=[ConstraintDetail({"type": "NOT_NULL"})])
        table_order_items = TableISR(name="order_items", columns=[col1, col2, col_qty])
        schema_isr = SchemaISR(tables=[table_order_items])

        ddl = convert_isr_to_postgresql_ddl(schema_isr)
        # print(f"\nComposite PK DDL (PostgreSQL):\n{ddl}")

        self.assertIn('CREATE TABLE "order_items" (', ddl)
        self.assertIn('    "order_id" INTEGER', ddl)
        self.assertIn('    "item_id" INTEGER', ddl)
        self.assertIn('    "quantity" INTEGER NOT NULL', ddl)
        self.assertIn('    PRIMARY KEY ("order_id", "item_id")', ddl)

if __name__ == "__main__":
    unittest.main()
