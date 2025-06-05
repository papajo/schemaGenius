# backend/tests/parsing_engine/parsers/test_sql_parser.py

import unittest
# Assuming tests are run from 'backend' directory or test runner handles paths
from app.core.parsing_engine.parsers.sql_parser import parse_sql_ddl_input, _map_sql_type_to_generic
from app.core.parsing_engine.intermediate_schema import SchemaISR, TableISR, ColumnISR, ConstraintDetail

class TestSqlParser(unittest.TestCase):

    def test_map_sql_type_to_generic_basic(self):
        # Test direct mappings (base type only)
        self.assertEqual(_map_sql_type_to_generic("INT"), "INTEGER")
        self.assertEqual(_map_sql_type_to_generic("INTEGER"), "INTEGER")
        self.assertEqual(_map_sql_type_to_generic("BIGINT"), "BIG_INTEGER")
        self.assertEqual(_map_sql_type_to_generic("VARCHAR"), "STRING") # Base type
        self.assertEqual(_map_sql_type_to_generic("CHAR"), "STRING")   # Base type
        self.assertEqual(_map_sql_type_to_generic("TEXT"), "TEXT")
        self.assertEqual(_map_sql_type_to_generic("CLOB"), "TEXT")
        self.assertEqual(_map_sql_type_to_generic("DECIMAL"), "DECIMAL")
        self.assertEqual(_map_sql_type_to_generic("NUMERIC"), "DECIMAL")
        self.assertEqual(_map_sql_type_to_generic("FLOAT"), "FLOAT")
        self.assertEqual(_map_sql_type_to_generic("REAL"), "FLOAT")
        self.assertEqual(_map_sql_type_to_generic("DOUBLE"), "FLOAT") #DOUBLE PRECISION also maps to FLOAT
        self.assertEqual(_map_sql_type_to_generic("BOOLEAN"), "BOOLEAN")
        self.assertEqual(_map_sql_type_to_generic("DATE"), "DATE")
        self.assertEqual(_map_sql_type_to_generic("TIME"), "TIME")
        self.assertEqual(_map_sql_type_to_generic("DATETIME"), "DATETIME")
        self.assertEqual(_map_sql_type_to_generic("TIMESTAMP"), "TIMESTAMP")
        self.assertEqual(_map_sql_type_to_generic("BLOB"), "BLOB")
        self.assertEqual(_map_sql_type_to_generic("BINARY"), "BLOB")
        self.assertEqual(_map_sql_type_to_generic("JSON"), "JSON_TYPE")
        self.assertEqual(_map_sql_type_to_generic("JSONB"), "JSON_TYPE")
        self.assertEqual(_map_sql_type_to_generic("UUID"), "UUID_TYPE")
        # Test with parameters (should still map base type)
        self.assertEqual(_map_sql_type_to_generic("VARCHAR", ["255"]), "STRING")
        self.assertEqual(_map_sql_type_to_generic("DECIMAL", ["10", "2"]), "DECIMAL")
        # Test fallback
        self.assertEqual(_map_sql_type_to_generic("UNSUPPORTED_TYPE"), "STRING")


    def test_simple_create_table(self):
        sql = """CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100) NOT NULL);"""
        schema_isr = parse_sql_ddl_input(sql)
        self.assertEqual(len(schema_isr.tables), 1, "Should parse one table.")
        table = schema_isr.tables[0]
        self.assertEqual(table.name, "users", "Table name should be 'users'.")
        self.assertEqual(len(table.columns), 2, "Table should have two columns.")

        id_col = next((c for c in table.columns if c.name == "id"), None)
        self.assertIsNotNone(id_col, "Column 'id' should exist.")
        self.assertEqual(id_col.generic_type, "INTEGER", "Column 'id' type should be INTEGER.")
        self.assertTrue(any(c.type == "PRIMARY_KEY" for c in id_col.constraints), "Column 'id' should have PRIMARY_KEY constraint.")

        name_col = next((c for c in table.columns if c.name == "name"), None)
        self.assertIsNotNone(name_col, "Column 'name' should exist.")
        self.assertEqual(name_col.generic_type, "STRING", "Column 'name' type should be STRING.") # VARCHAR(100) maps to STRING
        self.assertTrue(any(c.type == "NOT_NULL" for c in name_col.constraints), "Column 'name' should have NOT_NULL constraint.")

    def test_table_with_various_data_types_and_constraints(self):
        sql = """
        CREATE TABLE products (
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            sku VARCHAR(50) UNIQUE NOT NULL,
            description TEXT,
            price DECIMAL(10, 2) DEFAULT 0.00,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        schema_isr = parse_sql_ddl_input(sql)
        self.assertEqual(len(schema_isr.tables), 1)
        table = schema_isr.tables[0]
        self.assertEqual(table.name, "products")
        # Current parser might not perfectly get all 6 due to splitting logic, adjust as parser improves
        # For now, we'll check for specific columns we expect to be parsed somewhat correctly.

        product_id_col = next((c for c in table.columns if c.name == "product_id"), None)
        self.assertIsNotNone(product_id_col)
        self.assertEqual(product_id_col.generic_type, "INTEGER")
        self.assertTrue(any(c.type == "PRIMARY_KEY" for c in product_id_col.constraints))
        self.assertTrue(any(c.type == "AUTO_INCREMENT" for c in product_id_col.constraints))

        sku_col = next((c for c in table.columns if c.name == "sku"), None)
        self.assertIsNotNone(sku_col)
        self.assertEqual(sku_col.generic_type, "STRING") # VARCHAR(50)
        self.assertTrue(any(c.type == "UNIQUE" for c in sku_col.constraints))
        self.assertTrue(any(c.type == "NOT_NULL" for c in sku_col.constraints))

        description_col = next((c for c in table.columns if c.name == "description"), None)
        self.assertIsNotNone(description_col)
        self.assertEqual(description_col.generic_type, "TEXT")


        price_col = next((c for c in table.columns if c.name == "price"), None)
        self.assertIsNotNone(price_col)
        self.assertEqual(price_col.generic_type, "DECIMAL")
        default_constraint = next((c for c in price_col.constraints if c.type == "DEFAULT"), None)
        self.assertIsNotNone(default_constraint)
        self.assertEqual(default_constraint.details.get("value"), 0.00)

        is_active_col = next((c for c in table.columns if c.name == "is_active"), None)
        self.assertIsNotNone(is_active_col)
        self.assertEqual(is_active_col.generic_type, "BOOLEAN")
        default_constraint_active = next((c for c in is_active_col.constraints if c.type == "DEFAULT"), None)
        self.assertIsNotNone(default_constraint_active)
        self.assertEqual(default_constraint_active.details.get("value"), True)

        created_at_col = next((c for c in table.columns if c.name == "created_at"), None)
        self.assertIsNotNone(created_at_col)
        self.assertEqual(created_at_col.generic_type, "DATETIME")
        default_constraint_ts = next((c for c in created_at_col.constraints if c.type == "DEFAULT"), None)
        self.assertIsNotNone(default_constraint_ts)
        self.assertEqual(str(default_constraint_ts.details.get("value")).upper(), "CURRENT_TIMESTAMP")


    def test_multiple_create_table_statements(self):
        sql = """
        CREATE TABLE t1 (c1 INT);
        -- This is a comment
        CREATE TABLE t2 (c2 VARCHAR(10));
        /* Another comment */
        CREATE TABLE IF NOT EXISTS t3 (c3 TEXT);
        """
        schema_isr = parse_sql_ddl_input(sql)
        self.assertEqual(len(schema_isr.tables), 3)
        self.assertEqual(schema_isr.tables[0].name, "t1")
        self.assertEqual(schema_isr.tables[1].name, "t2")
        self.assertEqual(schema_isr.tables[2].name, "t3")

    def test_quoted_identifiers(self):
        # Using different quote types
        sql = 'CREATE TABLE "my table" (`my column` INT, "another col" TEXT, `yet-another-col` VARCHAR(20));'
        schema_isr = parse_sql_ddl_input(sql)
        self.assertEqual(len(schema_isr.tables), 1, "Should parse one table with quoted identifiers.")
        table = schema_isr.tables[0]
        self.assertEqual(table.name, "my table", "Table name with double quotes.")

        self.assertEqual(len(table.columns), 3, "Should parse three columns.")

        my_column = next((c for c in table.columns if c.name == "my column"), None)
        self.assertIsNotNone(my_column, "Column 'my column' (backticks) should exist.")
        self.assertEqual(my_column.generic_type, "INTEGER")

        another_col = next((c for c in table.columns if c.name == "another col"), None)
        self.assertIsNotNone(another_col, "Column 'another col' (double quotes) should exist.")
        self.assertEqual(another_col.generic_type, "TEXT") # TEXT maps to TEXT

        yac_col = next((c for c in table.columns if c.name == "yet-another-col"), None)
        self.assertIsNotNone(yac_col, "Column 'yet-another-col' (backticks) should exist.")
        self.assertEqual(yac_col.generic_type, "STRING")


    def test_incomplete_ddl_statement(self):
        sql = "CREATE TABLE incomplete_table (col1 INT" # Missing closing parenthesis and semicolon
        # The current parser might create a table with one column or an empty column list,
        # or even an empty table list if the statement is too broken to identify the table.
        # It should not crash.
        try:
            schema_isr = parse_sql_ddl_input(sql)
            if schema_isr.tables: # If a table was identified
                self.assertEqual(schema_isr.tables[0].name, "incomplete_table")
                # Depending on parser robustness, columns might be empty or partially parsed
                if schema_isr.tables[0].columns:
                    self.assertEqual(schema_isr.tables[0].columns[0].name, "col1")
                    self.assertEqual(schema_isr.tables[0].columns[0].generic_type, "INTEGER")
            # else: # If no table was identified due to severe malformation
                # self.assertEqual(len(schema_isr.tables), 0)
                # This depends on how the parser handles very broken DDL.
                # For now, not asserting len(schema_isr.tables) == 0 as it might find the table name.
        except Exception as e:
            self.fail(f"Parsing incomplete DDL raised an unexpected exception: {e}")

    def test_type_with_spaces_like_double_precision(self):
        sql = "CREATE TABLE float_test (val DOUBLE PRECISION);"
        schema_isr = parse_sql_ddl_input(sql)
        self.assertEqual(len(schema_isr.tables),1)
        table = schema_isr.tables[0]
        self.assertEqual(table.columns[0].name, "val")
        self.assertEqual(table.columns[0].generic_type, "FLOAT")

if __name__ == "__main__":
    unittest.main()
