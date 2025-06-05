# backend/app/schemas/request_models.py

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class SchemaGenerationRequest(BaseModel):
    input_data: str = Field(..., description="The raw input data (e.g., JSON string, SQL DDL, natural language text).")
    input_type: str = Field(..., description="Type of the input data provided.", examples=["json", "sql", "text"])
    target_db: Optional[str] = Field(None, description="Target database system for DDL generation (e.g., mysql, postgresql). Required if DDL output is expected.", examples=["mysql", "postgresql"])

    class Config:
        json_schema_extra = {
            "examples": [ # Changed to a list of examples
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
