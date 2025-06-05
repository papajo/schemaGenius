# backend/app/schemas/request_models.py

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class SchemaGenerationRequest(BaseModel):
    input_data: str = Field(..., description="The raw input data (e.g., JSON string, SQL DDL, CSV data, Python ORM code, natural language text).")
    input_type: str = Field(..., description="Type of the input data provided.",
                            examples=["json", "sql", "csv", "python", "sqlalchemy", "text"]) # Added python, sqlalchemy
    target_db: Optional[str] = Field(None, description="Target database system for DDL generation.",
                                     examples=["mysql", "postgresql", "postgres"])
    source_name: Optional[str] = Field(None, description="Optional name for the source, e.g., filename or suggested table name, especially for CSV or uploaded files.",
                                       examples=["my_data.csv", "user_table_from_csv"])

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "summary": "JSON to MySQL Example",
                    "description": "Generate MySQL DDL from a JSON schema definition.",
                    "value": {
                        "input_data": "{\"schema_name\": \"MyJSON_DB\", \"tables\": [{\"name\": \"items\", \"columns\": [{\"name\": \"item_id\", \"generic_type\": \"INTEGER\"}]}]}",
                        "input_type": "json",
                        "target_db": "mysql"
                    }
                },
                {
                    "summary": "SQL to PostgreSQL Example",
                    "description": "Generate PostgreSQL DDL from SQL CREATE TABLE statements.",
                    "value": {
                        "input_data": "CREATE TABLE products (product_id SERIAL PRIMARY KEY, product_name TEXT NOT NULL);",
                        "input_type": "sql",
                        "target_db": "postgresql"
                    }
                },
                {
                    "summary": "CSV to MySQL Example",
                    "description": "Generate MySQL DDL from CSV data. First row is headers.",
                    "value": {
                        "input_data": "sku,item_name,price\nS100,Widget,9.99\nS101,Gadget,19.99",
                        "input_type": "csv",
                        "target_db": "mysql",
                        "source_name": "inventory_from_csv"
                    }
                },
                {
                    "summary": "Python (SQLAlchemy) to MySQL Example",
                    "description": "Generate MySQL DDL from Python SQLAlchemy model definitions.",
                    "value": {
                        "input_data": "from sqlalchemy import Column, Integer, String\\nfrom sqlalchemy.orm import declarative_base\\nBase = declarative_base()\\nclass User(Base):\\n    __tablename__ = 'app_users'\\n    id = Column(Integer, primary_key=True)\\n    username = Column(String(50), nullable=False, unique=True)",
                        "input_type": "python", # or "sqlalchemy"
                        "target_db": "mysql"
                    }
                },
                { # Keep the NLP placeholder example if desired
                    "summary": "Text Input Example (Placeholder for NLP)",
                    "description": "Generate schema from a natural language description (future feature).",
                    "value": {
                        "input_data": "I need a table for blog posts with fields for id, title, and content.",
                        "input_type": "text",
                        "target_db": "postgresql"
                    }
                }
            ]
        }
