# backend/app/schemas/request_models.py

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class SchemaGenerationRequest(BaseModel):
    input_data: str = Field(..., description="The raw input data (e.g., JSON string, SQL DDL, natural language text).")
    input_type: str = Field(..., description="Type of the input data provided.", examples=["json", "sql", "text"])
    target_db: Optional[str] = Field(None, description="Target database system for DDL generation (e.g., mysql, postgresql). Required if DDL output is expected.", examples=["mysql", "postgresql"])

    class Config:
        json_schema_extra = {
            "example": {
                "input_data": "{\\"schema_name\\": \\"MyTestDB\\", \\"tables\\": [{\\"name\\": \\"users\\", \\"columns\\": [{\\"name\\": \\"id\\\", \\"generic_type\\": \\"INTEGER\\"}]}]}",
                "input_type": "json",
                "target_db": "mysql"
            }
        }
