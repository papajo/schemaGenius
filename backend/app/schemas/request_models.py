# backend/app/schemas/request_models.py

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class SchemaGenerationRequest(BaseModel):
    input_data: str = Field(..., description="The raw input data (e.g., JSON string, SQL DDL, CSV data, natural language text).")
    input_type: str = Field(..., description="Type of the input data provided.", examples=["json", "sql", "csv", "text"])
    target_db: Optional[str] = Field(None, description="Target database system for DDL generation (e.g., mysql, postgresql). Required if DDL output is expected.", examples=["mysql", "postgresql"])
    source_name: Optional[str] = Field(None, description="Optional name for the source, e.g., filename or suggested table name, especially for CSV or uploaded files.", examples=["my_data.csv", "user_table_from_csv"])

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "summary": "JSON Input Example",
                    "description": "Generate schema from a JSON string defining tables and columns.",
                    "value": {
                        "input_data": "{\"schema_name\": \"MyTestDB\", \"tables\": [{\"name\": \"users\", \"columns\": [{\"name\": \"id\", \"generic_type\": \"INTEGER\"}]}]}",
                        "input_type": "json",
                        "target_db": "mysql"
                    }
                },
                {
                    "summary": "SQL DDL Input Example",
                    "description": "Generate schema from SQL DDL CREATE TABLE statements.",
                    "value": {
                        "input_data": "CREATE TABLE products (product_id INT PRIMARY KEY, name VARCHAR(100) NOT NULL);\nCREATE TABLE categories (category_id INT PRIMARY KEY, category_name VARCHAR(50));",
                        "input_type": "sql",
                        "target_db": "mysql"
                    }
                },
                {
                    "summary": "CSV Input Example",
                    "description": "Generate schema from CSV data. The first row is assumed to be headers.",
                    "value": {
                        "input_data": "id,name,age\n1,Alice,30\n2,Bob,24\n3,Charlie,22",
                        "input_type": "csv",
                        "target_db": "mysql",
                        "source_name": "customers_data" # Example source_name for CSV
                    }
                },
                { # Keep the NLP placeholder example
                    "summary": "Text Input Example (Placeholder for NLP)",
                    "description": "Generate schema from a natural language description (future feature).",
                    "value": {
                        "input_data": "I need a table for customers with id, name, and email. Also a table for orders with order_id and customer_id.",
                        "input_type": "text",
                        "target_db": "postgresql"
                    }
                }
            ]
        }
