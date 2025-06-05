# backend/app/schemas/request_models.py

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class SchemaGenerationRequest(BaseModel):
    input_data: str = Field(..., description="The raw input data (e.g., JSON string, SQL DDL, CSV data, natural language text).")
    input_type: str = Field(..., description="Type of the input data provided.", examples=["json", "sql", "csv", "text"])
    # Added "postgres" as an alias example for PostgreSQL
    target_db: Optional[str] = Field(None, description="Target database system for DDL generation.", examples=["mysql", "postgresql", "postgres"])
    source_name: Optional[str] = Field(None, description="Optional name for the source, e.g., filename or suggested table name, especially for CSV or uploaded files.", examples=["my_data.csv", "user_table_from_csv"])

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "summary": "JSON to MySQL Example",
                    "description": "Generate MySQL DDL from a JSON schema definition.",
                    "value": {
                        "input_data": "{\"schema_name\": \"MyTestDB_MySQL\", \"tables\": [{\"name\": \"users\", \"columns\": [{\"name\": \"id\", \"generic_type\": \"INTEGER\", \"constraints\":[{\"type\":\"PRIMARY_KEY\"}]}]}]}",
                        "input_type": "json",
                        "target_db": "mysql"
                    }
                },
                {
                    "summary": "SQL to PostgreSQL Example",
                    "description": "Generate PostgreSQL DDL from SQL CREATE TABLE statements.",
                    "value": {
                        "input_data": "CREATE TABLE items (item_id SERIAL PRIMARY KEY, item_name TEXT NOT NULL, category VARCHAR(100));",
                        "input_type": "sql",
                        "target_db": "postgresql" # Or "postgres"
                    }
                },
                {
                    "summary": "CSV to MySQL Example",
                    "description": "Generate MySQL DDL from CSV data. First row is headers.",
                    "value": {
                        "input_data": "id,product_name,price\n1,SuperWidget,19.99\n2,MegaDevice,29.99",
                        "input_type": "csv",
                        "target_db": "mysql",
                        "source_name": "inventory_data"
                    }
                },
                 {
                    "summary": "JSON to PostgreSQL Example",
                    "description": "Generate PostgreSQL DDL from a JSON schema definition.",
                    "value": {
                        "input_data": "{\"schema_name\": \"MyTestDB_PG\", \"tables\": [{\"name\": \"events\", \"columns\": [{\"name\": \"event_id\", \"generic_type\": \"INTEGER\", \"constraints\":[{\"type\":\"PRIMARY_KEY\"}, {\"type\":\"AUTO_INCREMENT\"}]}, {\"name\":\"event_data\", \"generic_type\":\"JSON_TYPE\"}]}]}",
                        "input_type": "json",
                        "target_db": "postgresql"
                    }
                }
                # Placeholder for NLP example can remain if desired
            ]
        }
