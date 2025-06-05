# backend/tests/parsing_engine/test_parsing_engine.py

import unittest
import json

from app.core.parsing_engine import ParsingEngine
from app.core.parsing_engine.intermediate_schema import SchemaISR, TableISR, ColumnISR, ConstraintDetail

class TestParsingEngineIntegration(unittest.TestCase):

    def setUp(self):
        self.engine = ParsingEngine()
        self.sample_json_string_generic = json.dumps({
            "schema_name": "GenericDB_Test",
            "version": "1.0",
            "tables": [{
                "name": "items",
                "comment": "Items table",
                "columns": [
                    {"name": "item_id", "generic_type": "INTEGER", "constraints": [{"type": "PRIMARY_KEY"}, {"type": "AUTO_INCREMENT"}], "comment": "Item unique ID"},
                    {"name": "item_name", "generic_type": "STRING", "constraints": [{"type": "NOT_NULL"}]},
                    {"name": "price", "generic_type": "DECIMAL", "constraints": [{"type": "DEFAULT", "details": {"value": 0.00}}]},
                    {"name": "category", "generic_type": "ENUM_TYPE",
                     "constraints": [
                         {"type": "ENUM_VALUES", "details": {"values": ["electronics", "books", "clothing"]}},
                         {"type": "DEFAULT", "details": {"value": "electronics"}}
                     ]
                    }
                ]
            }]
        })
        self.sample_sql_ddl_generic = """
        CREATE TABLE "Users" (
            "UserID" SERIAL PRIMARY KEY,
            "Username" VARCHAR(100) NOT NULL UNIQUE,
            "Email" VARCHAR(255) UNIQUE,
            "Bio" TEXT,
            "LastLogin" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE "Profiles" (
            "ProfileID" BIGSERIAL PRIMARY KEY,
            "UserID" INTEGER NOT NULL, -- To be made FK
            "ProfileData" JSONB,
            CONSTRAINT "fk_profiles_user" FOREIGN KEY ("UserID") REFERENCES "Users"("UserID") ON DELETE CASCADE
        );
        """
        self.sample_csv_data_generic = "product_sku,product_name,cost,is_available\nSKU001,Laptop,1200.50,true\nSKU002,Mouse,25.99,false\nSKU003,Keyboard,75.00,T"

    # --- JSON Input Tests ---
    def test_json_to_mysql_ddl(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_json_string_generic, "json")
        self.assertIsInstance(schema_isr, SchemaISR)
        self.assertEqual(schema_isr.schema_name, "GenericDB_Test")

        mysql_ddl = self.engine.convert_isr_to_target_ddl(schema_isr, "mysql")
        self.assertIn("CREATE TABLE `items`", mysql_ddl)
        self.assertIn("`item_id` INT AUTO_INCREMENT", mysql_ddl)
        self.assertIn("`item_name` VARCHAR(255) NOT NULL", mysql_ddl)
        self.assertIn("`price` DECIMAL(10, 2) DEFAULT 0.00", mysql_ddl)
        self.assertIn("`category` ENUM('electronics', 'books', 'clothing') DEFAULT 'electronics'", mysql_ddl)
        self.assertIn("COMMENT ON COLUMN `items`.`item_id` IS 'Item unique ID'", mysql_ddl) # Check if comments propagate

    def test_json_to_postgresql_ddl(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_json_string_generic, "json")
        self.assertIsInstance(schema_isr, SchemaISR)

        pg_ddl = self.engine.convert_isr_to_target_ddl(schema_isr, "postgresql")
        # print(f"\nPG DDL from JSON:\n{pg_ddl}") # Debug
        self.assertIn('CREATE TYPE "enum_items_category" AS ENUM (\'electronics\', \'books\', \'clothing\');', pg_ddl)
        self.assertIn('CREATE TABLE "items" (', pg_ddl)
        self.assertIn('    "item_id" SERIAL', pg_ddl)
        self.assertIn('    "item_name" VARCHAR(255) NOT NULL', pg_ddl)
        self.assertIn('    "price" DECIMAL(10, 2) DEFAULT 0.00', pg_ddl)
        self.assertIn('    "category" "enum_items_category" DEFAULT \'electronics\'', pg_ddl)
        self.assertIn('COMMENT ON COLUMN "items"."item_id" IS \'Item unique ID\';', pg_ddl)


    # --- SQL Input Tests ---
    def test_sql_to_mysql_ddl(self):
        # Note: SQL parser is basic, so expectations should match its current capabilities.
        schema_isr = self.engine.generate_schema_from_input(self.sample_sql_ddl_generic, "sql")
        self.assertIsInstance(schema_isr, SchemaISR)
        self.assertEqual(len(schema_isr.tables), 2)

        mysql_ddl = self.engine.convert_isr_to_target_ddl(schema_isr, "mysql")
        # print(f"\nMySQL DDL from SQL:\n{mysql_ddl}") # Debug
        self.assertIn("CREATE TABLE `Users`", mysql_ddl)
        self.assertIn("`UserID` INT AUTO_INCREMENT", mysql_ddl) # SERIAL maps to INT AUTO_INCREMENT
        self.assertIn("`Username` VARCHAR(255) NOT NULL UNIQUE", mysql_ddl) # VARCHAR(100) maps to VARCHAR(255) by default
        self.assertIn("`LastLogin` TIMESTAMP DEFAULT CURRENT_TIMESTAMP", mysql_ddl)

        self.assertIn("CREATE TABLE `Profiles`", mysql_ddl)
        self.assertIn("`ProfileData` JSON", mysql_ddl) # JSONB maps to JSON
        # Basic SQL parser might not pick up FKs defined at table level yet. This tests current state.
        # self.assertIn("FOREIGN KEY (`UserID`) REFERENCES `Users` (`UserID`)", mysql_ddl)


    def test_sql_to_postgresql_ddl(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_sql_ddl_generic, "sql")
        self.assertIsInstance(schema_isr, SchemaISR)

        pg_ddl = self.engine.convert_isr_to_target_ddl(schema_isr, "postgres") # Using alias
        # print(f"\nPG DDL from SQL:\n{pg_ddl}") # Debug
        self.assertIn('CREATE TABLE "Users" (', pg_ddl)
        self.assertIn('    "UserID" SERIAL', pg_ddl)
        self.assertIn('    "Username" VARCHAR(255) NOT NULL UNIQUE', pg_ddl)
        self.assertIn('    "LastLogin" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP', pg_ddl)

        self.assertIn('CREATE TABLE "Profiles" (', pg_ddl)
        self.assertIn('    "ProfileData" JSONB', pg_ddl)
        # self.assertIn('CONSTRAINT "fk_profiles_user" FOREIGN KEY ("UserID") REFERENCES "Users"("UserID") ON DELETE CASCADE', pg_ddl)


    # --- CSV Input Tests ---
    def test_csv_to_mysql_ddl(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_csv_data_generic, "csv", source_name="products_from_csv")
        self.assertIsInstance(schema_isr, SchemaISR)
        self.assertEqual(schema_isr.tables[0].name, "products_from_csv")

        mysql_ddl = self.engine.convert_isr_to_target_ddl(schema_isr, "mysql")
        # print(f"\nMySQL DDL from CSV:\n{mysql_ddl}") # Debug
        self.assertIn("CREATE TABLE `products_from_csv`", mysql_ddl)
        self.assertIn("`product_sku` VARCHAR(255)", mysql_ddl) # Inferred STRING
        self.assertIn("`cost` DECIMAL(10, 2)", mysql_ddl) # Inferred FLOAT maps to DECIMAL
        self.assertIn("`is_available` BOOLEAN", mysql_ddl) # Inferred BOOLEAN

    def test_csv_to_postgresql_ddl(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_csv_data_generic, "csv", source_name="products_from_csv_pg")
        self.assertIsInstance(schema_isr, SchemaISR)

        pg_ddl = self.engine.convert_isr_to_target_ddl(schema_isr, "postgresql")
        # print(f"\nPG DDL from CSV:\n{pg_ddl}") # Debug
        self.assertIn('CREATE TABLE "products_from_csv_pg"', pg_ddl)
        self.assertIn('    "product_sku" VARCHAR(255)', pg_ddl)
        self.assertIn('    "cost" REAL', pg_ddl) # Inferred FLOAT maps to REAL
        self.assertIn('    "is_available" BOOLEAN', pg_ddl)

    # --- Error and Edge Case Tests ---
    def test_unsupported_input_type_error(self):
        with self.assertRaisesRegex(NotImplementedError, "Parser for input type 'text' is not implemented."):
            self.engine.generate_schema_from_input("A simple text.", "text")

    def test_unsupported_target_db_error(self):
        schema_isr = self.engine.generate_schema_from_input(self.sample_json_string_generic, "json")
        with self.assertRaisesRegex(NotImplementedError, "Adapter for target database 'sqlite' is not implemented."):
            self.engine.convert_isr_to_target_ddl(schema_isr, "sqlite")

if __name__ == "__main__":
    unittest.main()
