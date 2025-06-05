# backend/tests/api/endpoints/test_generate.py

import json
from fastapi.testclient import TestClient
# Assuming tests are run from 'backend' directory or test runner handles paths
from app.main import app # Import the FastAPI app instance

client = TestClient(app)

class TestGenerateEndpoint:

    # Using pytest style tests (no self, direct asserts)
    def test_generate_schema_success_json_to_mysql(self):
        payload = {
            "input_data": json.dumps({
                "schema_name": "TestAPI_DB",
                "tables": [{
                    "name": "clients",
                    "columns": [
                        {"name": "id", "generic_type": "INTEGER", "constraints": [{"type": "PRIMARY_KEY"}]}
                    ]
                }]
            }),
            "input_type": "json",
            "target_db": "mysql"
        }
        response = client.post("/api/v1/schema/generate/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "output_ddl" in data
        assert data["output_ddl"] is not None
        assert "CREATE TABLE `clients`" in data["output_ddl"]
        assert data["input_type"] == "json"
        assert data["target_db"] == "mysql"
        assert "Schema DDL generated successfully." in data["message"]

    def test_generate_schema_unsupported_input_type(self):
        payload = {"input_data": "<schema></schema>", "input_type": "xml", "target_db": "mysql"}
        response = client.post("/api/v1/schema/generate/", json=payload)
        assert response.status_code == 501 # Not Implemented
        data = response.json()
        assert "Parser for input type 'xml' is not implemented." in data["detail"]

    def test_generate_schema_unsupported_target_db(self):
        payload = {"input_data": json.dumps({"tables": []}), "input_type": "json", "target_db": "oracle"}
        response = client.post("/api/v1/schema/generate/", json=payload)
        assert response.status_code == 501 # Not Implemented
        data = response.json()
        assert "Adapter for target database 'oracle' is not implemented." in data["detail"]

    def test_generate_schema_malformed_json_input(self):
        payload = {"input_data": '{"tables": [}', "input_type": "json", "target_db": "mysql"} # Malformed JSON
        response = client.post("/api/v1/schema/generate/", json=payload)
        assert response.status_code == 400 # Bad Request
        data = response.json()
        assert "Invalid JSON format" in data["detail"]

    def test_generate_schema_no_target_db(self):
        payload = {
            "input_data": json.dumps({
                "schema_name": "NoTarget",
                "tables": [{"name": "items", "columns": [{"name": "id", "generic_type": "INTEGER"}]}]
            }),
            "input_type": "json",
            "target_db": None # Explicitly None or omitted
        }
        response = client.post("/api/v1/schema/generate/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["output_ddl"] is None
        # Ensure the message reflects that DDL was not generated because target_db was None
        assert "Input processed, but no target_db specified for DDL generation." in data["message"]
        assert data["target_db"] is None

# To run these tests, navigate to the backend directory and run: pytest
# Ensure pytest and httpx are installed: pip install pytest httpx
