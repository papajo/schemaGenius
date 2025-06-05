# SchemaGenius - Automatic Database Schema Generation (Design Phase)

## Description

SchemaGenius is a planned application designed to automatically generate database schemas based on various user inputs. This includes code snippets (SQL, Python ORMs, Java JPA), natural language descriptions, and structured data files (CSV, JSON). The goal is to provide an intelligent, user-friendly tool that streamlines the initial phases of database design.

## Current Status

This repository currently contains the **initial design documents**, **basic project scaffolding**, and a **foundational API layer** for the SchemaGenius application. Key functionalities like JSON, basic SQL DDL, and CSV parsing, along with MySQL DDL generation, are implemented in the backend and accessible via an API endpoint.

## Design Documents

The core design of SchemaGenius is detailed in the following documents:

*   **`final_design_document.md`**: A comprehensive document consolidating all aspects of the application's design.
    *   `architecture.md`
    *   `parsing_engine_details.md`
    *   `ui_ux_design.md`
    *   `validation_error_handling.md`
    *   `export_formats_options.md`
    *   `scalability_performance.md`
    *   `application_documentation_structure.md`

## Project Structure

The initial project structure has been scaffolded as follows:

*   **`backend/`**: Contains the Python FastAPI backend application.
    *   `app/`: Main application code.
        *   `main.py`: FastAPI app initialization.
        *   `api/`: API endpoint definitions (e.g., schema generation).
        *   `core/`: Core logic, including the `parsing_engine/`.
            *   `parsing_engine/`: Modules for parsing inputs and generating schemas.
                *   `__init__.py`: Main `ParsingEngine` class.
                *   `intermediate_schema.py`: Defines `SchemaISR` and related classes.
                *   `parsers/`: Input-specific parsers (e.g., `json_parser.py`, `sql_parser.py`, `csv_parser.py`).
                *   `adapters/`: Database-specific DDL generators (e.g., `mysql_adapter.py`).
        *   `schemas/`: Pydantic models for API request/response validation.
    *   `requirements.txt`: Backend dependencies.
    *   `tests/`: Unit and integration tests for the backend.
        *   `api/`: Tests for API endpoints.
        *   `parsing_engine/`: Tests for parsing logic and adapters.

*   **`frontend/`**: Contains the React with TypeScript frontend application (currently placeholder).
    *   `public/`: Static assets and `index.html`.
    *   `src/`: Frontend source code (`.tsx` files, CSS, etc.).
    *   `package.json`: Frontend dependencies and scripts.
    *   `tsconfig.json`: TypeScript configuration.
    *   `.gitignore`: Node.js/React-specific ignore file.

*   **Design Documents**: All files ending with `.md` at the root level.

## Running the Backend & API

The backend is built using FastAPI. To run it locally:

1.  Navigate to the `backend/` directory:
    ```bash
    cd backend
    ```
2.  Create a virtual environment and activate it (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the Uvicorn server:
    ```bash
    uvicorn app.main:app --reload
    ```
The API will typically be available at `http://127.0.0.1:8000`. You can access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

### API Endpoints

**POST /api/v1/schema/generate/**

*   **Purpose**: Generates a database schema DDL based on the provided input.
*   **Request Body**: `SchemaGenerationRequest` (see `backend/app/schemas/request_models.py` and interactive `/docs`)
    *   `input_data` (string): The raw input (e.g., JSON string, SQL DDL statements, CSV data).
    *   `input_type` (string): Type of input (e.g., "json", "sql", "csv").
    *   `target_db` (string, optional): Target database (e.g., "mysql").
    *   `source_name` (string, optional): Suggested table name or source identifier (e.g., for CSV data, this might become the table name if provided).
*   **Response Body**: `SchemaGenerationResponse` (see `backend/app/schemas/response_models.py` and interactive `/docs`)
*   **Example `curl` request (JSON input)**:
    ```bash
    curl -X POST "http://127.0.0.1:8000/api/v1/schema/generate/" \
    -H "Content-Type: application/json" \
    -d '{
      "input_data": "{\"schema_name\": \"MyCurlDB\", \"tables\": [{\"name\": \"test_table\", \"columns\": [{\"name\": \"col1\", \"generic_type\": \"STRING\"}]}]}",
      "input_type": "json",
      "target_db": "mysql"
    }'
    ```
*   **Example `curl` request (SQL DDL input)**:
    ```bash
    curl -X POST "http://127.0.0.1:8000/api/v1/schema/generate/" \
    -H "Content-Type: application/json" \
    -d '{
      "input_data": "CREATE TABLE customers (id INT PRIMARY KEY, email VARCHAR(255) NOT NULL UNIQUE); CREATE TABLE orders (order_id INT PRIMARY KEY, customer_id INT);",
      "input_type": "sql",
      "target_db": "mysql"
    }'
    ```
*   **Example `curl` request (CSV input)**:
    ```bash
    curl -X POST "http://127.0.0.1:8000/api/v1/schema/generate/" \
    -H "Content-Type: application/json" \
    -d '{
      "input_data": "colA,colB,colC\n1,hello,true\n2,world,false",
      "input_type": "csv",
      "source_name": "my_data_from_csv",
      "target_db": "mysql"
    }'
    ```

## Future Work

The next phases for this project will involve:

1.  Implementing more advanced features for SQL and CSV parsers (e.g., foreign key detection from SQL `ALTER TABLE` statements, more robust CSV type inference and dialect handling).
2.  Implementing other parsers (Python ORM, NLP for natural language text, etc.).
3.  Implementing more adapters (PostgreSQL, MongoDB, etc.).
4.  Developing the frontend user interface for easier interaction.
5.  Enhancing error handling, validation, and schema enrichment capabilities.
6.  Adding features like schema visualization and direct editing.
7.  Thorough testing and iteration across all components.

---

*This README provides an overview of the SchemaGenius project, its current development status, and how to run the backend API.*
