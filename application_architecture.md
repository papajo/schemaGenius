# Application Architecture

This document outlines the architecture of the application, detailing its main components, suggested technology stack, communication flow, and data representation.

## 1. Main Components

The application is composed of the following main components:

*   **Frontend:**
    *   **Purpose:** User interaction, input gathering, schema visualization, and editing.
    *   **Responsibilities:** Render UI, handle user input, communicate with Backend API.
*   **Backend API:**
    *   **Purpose:** Core business logic, request handling, orchestration of parsing and generation.
    *   **Responsibilities:** Expose RESTful endpoints, manage user sessions (if any), interact with the Parsing Engine and Schema Generation Logic, communicate with the Database Interface.
*   **Parsing Engine:**
    *   **Purpose:** Analyze various user inputs (code, text, files).
    *   **Responsibilities:** Implement strategies for each input type, extract an intermediate representation of potential database entities. This might be a collection of microservices or a modular library.
*   **Schema Generation Logic:**
    *   **Purpose:** Convert the intermediate representation from the Parsing Engine into a formal database schema.
    *   **Responsibilities:** Apply database design principles, infer data types and relationships, translate the schema into target database system specifics.
*   **Database Interface:**
    *   **Purpose:** Abstract database operations for the application's own data (user accounts, projects).
    *   **Responsibilities:** Provide CRUD operations for application data, separate from the user-generated schemas.
*   **Task Queue / Worker System (Optional but Recommended):**
    *   **Purpose:** Handle long-running, resource-intensive tasks asynchronously.
    *   **Responsibilities:** Manage jobs like parsing large codebases or complex natural language descriptions, ensuring the API remains responsive.

## 2. Technology Stack Suggestions

The following technology stack is suggested for the development of the application:

*   **Frontend:** React (with Redux/Context API for state management), Vue.js (with Vuex), or Angular. Consider UI libraries like Material-UI or Ant Design for pre-built components.
*   **Backend API:**
    *   Python: Flask (lightweight, flexible) or Django (batteries-included).
    *   Node.js: Express.js (minimalist, fast I/O) with TypeScript for type safety.
*   **Parsing Engine:**
    *   Code Parsing: ANTLR (for generating parsers for SQL, Python, Java), or leverage existing language-specific parsers/linters.
    *   Natural Language Processing (NLP): Python with spaCy or NLTK.
    *   File Parsing: Standard libraries for CSV, JSON (e.g., Python's `csv` and `json` modules).
*   **Schema Generation Logic:** Implemented in the backend language (Python/Node.js). Focus on clear, rule-based logic.
*   **Application Database:** PostgreSQL (robust, feature-rich) or MySQL (widely used). For simpler needs, SQLite could be an option during early development.
*   **Task Queue:** Celery with RabbitMQ or Redis (if using Python backend). BullMQ or similar for Node.js.

## 3. Communication Flow

The communication between the components is as follows:

*   **User to Frontend:** User interacts via a web browser.
*   **Frontend to Backend API:** Primarily via HTTPS using RESTful API calls (e.g., `POST /api/v1/projects/{project_id}/parse_code`, `GET /api/v1/projects/{project_id}/schema`). JSON for data exchange.
*   **Backend API to Parsing Engine:** Internal function calls if monolithic, or RPC/message queue if microservices. The Parsing Engine returns a structured intermediate representation (e.g., a JSON object describing potential tables, columns, relationships).
*   **Backend API to Schema Generation Logic:** Internal function calls, passing the intermediate representation. The Logic returns a structured schema object (agnostic of specific DB syntax initially).
*   **Backend API to Database Interface:** Internal function calls to save/retrieve project data or user information.
*   **Backend API to Task Queue:** Enqueues tasks (e.g., `parse_large_file_task`) with necessary parameters. Workers pick up tasks and can update the application database or notify the Backend API upon completion (e.g., via webhooks or by updating a status in the database).

## 4. Data Representation (High-Level)

The data is represented at different stages as follows:

*   **Intermediate Representation (Post-Parsing):** A flexible structure (e.g., JSON) that captures entities, attributes, detected relationships, and confidence scores. Example:
    ```json
    {
      "entities": [
        { "name": "users", "attributes": ["id", "email"], "source": "code_snippet_1.py" },
        { "name": "posts", "attributes": ["title", "user_id"], "source": "text_description_1" }
      ],
      "potential_relationships": [
        { "from_entity": "posts", "from_attribute": "user_id", "to_entity": "users", "to_attribute": "id", "type": "many-to-one" }
      ]
    }
    ```
*   **Internal Schema Representation (Pre-Export):** A more formal structure that defines tables, columns with data types, primary keys, foreign keys, indexes, etc. This is then used to generate the final export formats.
