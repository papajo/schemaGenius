# SchemaGenius - Automatic Database Schema Generation

## Description
SchemaGenius is an application designed to automatically generate database schemas based on various user inputs. This includes code snippets (SQL, Python ORMs, Java JPA), natural language descriptions, and structured data files (CSV, JSON). The goal is to provide an intelligent, user-friendly tool that streamlines the initial phases of database design.

## Current Status

This repository currently contains the **initial design documents**, **project scaffolding for backend and frontend**, a **foundational API layer**, and a **basic frontend UI** for interaction. Key functionalities implemented include:
*   **Parsers**: JSON, basic SQL DDL, CSV, basic Python ORM (SQLAlchemy).
*   **Adapters**: MySQL DDL, PostgreSQL DDL.
*   **API**: Endpoint for schema generation.
*   **Frontend**: Basic input page (`InputPage.tsx`) to interact with the API via an `api.ts` service.

## Design Documents

The core design of SchemaGenius is detailed in the following documents:
*   **`final_design_document.md`**: A comprehensive document consolidating all aspects of the application's design.
    *   (Individual documents like `architecture.md`, `parsing_engine_details.md`, etc., are part of this consolidated document).

## Project Structure

The initial project structure has been scaffolded as follows:

*   **`backend/`**: Contains the Python FastAPI backend application.
    *   `app/`: Main application code.
        *   `main.py`: FastAPI app initialization.
        *   `api/`: API endpoint definitions.
        *   `core/`: Core logic, including the `parsing_engine/`.
            *   `parsing_engine/`: Modules for parsing inputs and generating schemas.
                *   `__init__.py`: Main `ParsingEngine` class.
                *   `intermediate_schema.py`: Defines `SchemaISR` and related classes.
                *   `parsers/`: Input-specific parsers (e.g., `json_parser.py`, `sql_parser.py`, `csv_parser.py`, `python_orm_parser.py`).
                *   `adapters/`: Database-specific DDL generators (e.g., `mysql_adapter.py`, `postgresql_adapter.py`).
        *   `schemas/`: Pydantic models for API request/response validation.
    *   `requirements.txt`: Backend dependencies.
    *   `tests/`: Unit and integration tests for the backend.

*   **`frontend/`**: Contains the React with TypeScript frontend application.
    *   `public/`: Static assets and `index.html`.
    *   `src/`: Frontend source code.
        *   `App.tsx`: Main React application component, renders `InputPage`.
        *   `index.tsx`: React DOM entry point.
        *   `pages/InputPage.tsx`: Main UI for submitting schema generation requests.
        *   `services/api.ts`: Module for backend API communication using `axios`.
        *   `components/`: (Currently empty) For reusable UI components.
        *   `assets/`: (Currently empty) For static assets like images, fonts.
    *   `package.json`: Frontend dependencies and scripts (includes `axios`).
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

## Running the Frontend

The frontend is a React application created with Create React App (TypeScript).

1.  Ensure the backend API is running (see section above).
2.  Navigate to the `frontend/` directory (in a new terminal window):
    ```bash
    cd frontend
    ```
3.  Install dependencies (if you haven't already):
    ```bash
    npm install
    # or
    # yarn install
    ```
4.  Start the frontend development server:
    ```bash
    npm start
    # or
    # yarn start
    ```
This will usually open the application in your default web browser at `http://localhost:3000`. You should see the `InputPage` interface.

## API Endpoints

**POST /api/v1/schema/generate/**

*   **Purpose**: Generates a database schema DDL based on the provided input.
*   **Request Body**: `SchemaGenerationRequest` (see `backend/app/schemas/request_models.py` and interactive `/docs`)
    *   `input_data` (string): The raw input (e.g., JSON string, SQL DDL statements, CSV data, Python ORM code).
    *   `input_type` (string): Type of input (e.g., "json", "sql", "csv", "python", "sqlalchemy").
    *   `target_db` (string, optional): Target database (e.g., "mysql", "postgresql", "postgres").
    *   `source_name` (string, optional): Suggested table name or source identifier (e.g., for CSV data).
*   **Response Body**: `SchemaGenerationResponse` (see `backend/app/schemas/response_models.py` and interactive `/docs`)
*   **Example `curl` requests**: (Refer to `/docs` on the running server for detailed, executable examples. Basic examples for different input types are provided in the API schema documentation.)

## Future Work

The next phases for this project will involve:

1.  **Frontend Enhancements**: Implementing schema visualization, a more polished UI/UX based on `ui_ux_design.md`, schema editing capabilities, and project management.
2.  **Backend Parser Enhancements**: Adding more advanced features to existing parsers (SQL: foreign keys from `ALTER TABLE`, indexes, complex constraints; CSV: more robust type inference, dialect options; Python ORM: relationship parsing, `__table_args__`).
3.  **New Parsers**: Implementing parsers for Java JPA, NLP for natural language text.
4.  **New Adapters**: Adding support for MongoDB, SQL Server, etc.
5.  **Core Engine**: Improving error handling and validation based on `validation_error_handling.md`, and adding schema enrichment logic.
6.  **Deployment**: Setting up CI/CD pipelines and deployment strategies as per `architecture.md` and `scalability_performance.md`.
7.  **Documentation**: Populating the user documentation based on `application_documentation_structure.md`.
8.  Thorough testing and iteration across all components.

---

*This README provides an overview of the SchemaGenius project, its current development status, and how to run the backend API and basic frontend.*
