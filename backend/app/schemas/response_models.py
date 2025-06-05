# backend/app/schemas/response_models.py

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class SchemaGenerationResponse(BaseModel):
    output_ddl: Optional[str] = Field(None, description="The generated Data Definition Language (DDL) string for the target database.")
    schema_isr_data: Optional[Dict[str, Any]] = Field(None, description="A dictionary representation of the Intermediate Schema Representation (ISR). Could be large.")
    input_type: str = Field(..., description="The type of input data that was processed.")
    target_db: Optional[str] = Field(None, description="The target database for which DDL was generated.")
    message: Optional[str] = Field(None, description="General message, e.g., success or informational.")
    error_message: Optional[str] = Field(None, description="Error message if the process failed.")

    class Config:
        json_schema_extra = {
            "example": {
                "output_ddl": "CREATE TABLE users (id INT);",
                "input_type": "json",
                "target_db": "mysql",
                "message": "Schema generated successfully."
            }
        }

class ISRSchemaResponse(BaseModel): # Kept separate for now, might merge or refine
    schema_isr_data: Dict[str, Any] = Field(..., description="A dictionary representation of the Intermediate Schema Representation (ISR).")
    message: Optional[str] = Field(None, description="General message.")
