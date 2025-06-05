# backend/app/api/endpoints/generate.py

from fastapi import APIRouter, HTTPException, status
from typing import Optional

# Corrected import paths to be relative to the 'app' directory,
# assuming 'backend/app' is the main application package.
from app.schemas.request_models import SchemaGenerationRequest
from app.schemas.response_models import SchemaGenerationResponse
from app.core.parsing_engine import ParsingEngine
from app.core.parsing_engine.intermediate_schema import SchemaISR # For type hinting if needed

router = APIRouter()
# Initialize engine once. For production, consider FastAPI dependency injection.
parsing_engine = ParsingEngine()

@router.post("/schema/generate/", response_model=SchemaGenerationResponse, status_code=status.HTTP_200_OK)
async def generate_schema_endpoint(request: SchemaGenerationRequest) -> SchemaGenerationResponse:
    """
    Receives schema generation request, processes it using the ParsingEngine,
    and returns the generated DDL or an error message.
    """
    try:
        # Step 1: Generate Intermediate Schema Representation (ISR)
        # Pass source_name from the request to the parsing engine
        schema_isr: SchemaISR = parsing_engine.generate_schema_from_input(
            input_data=request.input_data,
            input_type=request.input_type,
            source_name=request.source_name # Pass the new source_name field
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
                # schema_isr_data=schema_isr.to_dict() # Consider if ISR should be returned
            )
        else:
            # If no target_db, just acknowledge processing and potentially return ISR
            return SchemaGenerationResponse(
                input_type=request.input_type,
                target_db=request.target_db, # Will be None
                message="Input processed to Intermediate Schema Representation. No target_db specified for DDL generation."
                # schema_isr_data=schema_isr.to_dict() # Consider if ISR should be returned
            )

    except NotImplementedError as e:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(e))
    except ValueError as e:
        # ValueError could come from json_parser or csv_parser for bad input structure
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e: # Catch-all for other unexpected errors
        # Log the exception details in a real application
        print(f"Unexpected error in generate_schema_endpoint: {e}") # For debugging
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during schema generation.")
