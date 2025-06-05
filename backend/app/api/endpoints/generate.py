# backend/app/api/endpoints/generate.py

from fastapi import APIRouter, HTTPException, status
from typing import Optional # Added Optional for output_ddl
from app.schemas.request_models import SchemaGenerationRequest
from app.schemas.response_models import SchemaGenerationResponse
from app.core.parsing_engine import ParsingEngine
from app.core.parsing_engine.intermediate_schema import SchemaISR # For type hinting

router = APIRouter()
# Initialize engine once. For production, consider FastAPI dependency injection for better management.
parsing_engine = ParsingEngine()

@router.post("/schema/generate/", response_model=SchemaGenerationResponse, status_code=status.HTTP_200_OK)
async def generate_schema_endpoint(request: SchemaGenerationRequest) -> SchemaGenerationResponse:
    """
    Receives schema generation request, processes it using the ParsingEngine,
    and returns the generated DDL or an error message.
    """
    try:
        # Step 1: Generate Intermediate Schema Representation (ISR)
        schema_isr: SchemaISR = parsing_engine.generate_schema_from_input(
            input_data=request.input_data,
            input_type=request.input_type
        )

        output_ddl: Optional[str] = None
        # Step 2: Convert ISR to target DDL if target_db is specified
        if request.target_db:
            output_ddl = parsing_engine.convert_isr_to_target_ddl(
                isr=schema_isr,
                target_db=request.target_db
            )
            return SchemaGenerationResponse(
                output_ddl=output_ddl,
                input_type=request.input_type,
                target_db=request.target_db,
                message="Schema DDL generated successfully."
            )
        else:
            # If no target_db, return ISR data (or a message)
            # Convert ISR to dict for JSON response (Pydantic does this automatically for nested models if they are Pydantic models)
            # For now, let us assume a simple dict conversion or that ISR itself is serializable
            # This part might need refinement based on how SchemaISR is structured and if it needs a .dict() method
            return SchemaGenerationResponse(
                input_type=request.input_type,
                target_db=request.target_db, # Will be None
                message="Input processed to Intermediate Schema Representation. No target_db specified for DDL generation.",
                # schema_isr_data=schema_isr.to_dict() # Assuming a to_dict() method or Pydantic serializes it
            )

    except NotImplementedError as e:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e: # Catch-all for other unexpected errors
        # Log the exception details in a real application: logging.exception(e)
        print(f"Unexpected error in generate_schema_endpoint: {e}") # For debugging during scaffolding
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")
