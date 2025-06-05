// frontend/src/services/api.ts
import axios, { AxiosError, AxiosResponse } from "axios";

// Base URL for the API.
// It attempts to read from an environment variable (REACT_APP_API_BASE_URL),
// defaulting to localhost:8000 if not set. This is common for Create React App.
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000/api/v1";

/**
 * Payload for the schema generation API endpoint.
 * Matches the Pydantic model `SchemaGenerationRequest` in the backend.
 */
export interface GenerateSchemaPayload {
  input_data: string;
  input_type: string; // e.g., "json", "sql", "csv", "python"
  target_db?: string;  // e.g., "mysql", "postgresql"
  source_name?: string; // Optional, e.g., filename for CSV
}

/**
 * Expected data structure for a successful response from the /schema/generate/ endpoint.
 * Matches the Pydantic model `SchemaGenerationResponse` in the backend.
 */
export interface GenerateSchemaResponseData {
  output_ddl?: string;
  schema_isr_data?: Record<string, any>; // Represents the Intermediate Schema Representation
  input_type: string; // Will be echoed back from the request
  target_db?: string; // Will be echoed back if provided
  message?: string;
  error_message?: string; // This field will be populated by our catch block on error
}

/**
 * Structure for error details that might come from the FastAPI backend
 * (e.g., validation errors or HTTPException details).
 */
export interface ApiErrorDetail {
  detail: string | Record<string, any>; // FastAPI often returns {"detail": "message"} or structured error
}

/**
 * Makes an API call to the backend's /schema/generate/ endpoint.
 *
 * @param payload - The data to send for schema generation.
 * @returns A Promise that resolves to the response data from the API.
 *          In case of an error, it returns an object conforming to
 *          GenerateSchemaResponseData with an `error_message` field populated.
 */
export const generateSchemaAPI = async (payload: GenerateSchemaPayload): Promise<GenerateSchemaResponseData> => {
  try {
    const response: AxiosResponse<GenerateSchemaResponseData> =
      await axios.post<GenerateSchemaResponseData>(`${API_BASE_URL}/schema/generate/`, payload);
    // Ensure that even on successful API call, if backend sends an error_message, it's preserved.
    // Pydantic models might not have error_message on success, so this might mostly be for client-side errors.
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<ApiErrorDetail>;
    let errorMsg = "An unexpected error occurred while calling the API.";

    if (axiosError.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      if (axiosError.response.data && axiosError.response.data.detail) {
        if (typeof axiosError.response.data.detail === "string") {
          errorMsg = axiosError.response.data.detail;
        } else {
          // If detail is an object (e.g. Pydantic validation error details)
          errorMsg = JSON.stringify(axiosError.response.data.detail);
        }
      } else {
        // Fallback if detail is not in the expected structure
        errorMsg = `Error ${axiosError.response.status}: ${axiosError.response.statusText || 'Server error'}`;
      }
    } else if (axiosError.request) {
      // The request was made but no response was received
      errorMsg = "No response received from the server. Please check your network connection and the API server status.";
    } else {
      // Something happened in setting up the request that triggered an Error
      errorMsg = axiosError.message || "Error in setting up API request.";
    }

    console.error("API Call Error:", errorMsg, error); // Log the full error for debugging

    // Return an object that fits the GenerateSchemaResponseData structure,
    // indicating an error occurred by populating error_message.
    return {
      error_message: errorMsg,
      input_type: payload.input_type, // Echo back input params for context
      target_db: payload.target_db,
      // other fields like output_ddl, schema_isr_data, message will be undefined
    };
  }
};

// Example of how this might be used in a React component:
/*
import React, { useState, useEffect } from 'react';
import { generateSchemaAPI, GenerateSchemaPayload, GenerateSchemaResponseData } from './api'; // Adjust path as needed

const SchemaGeneratorComponent: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [apiResponse, setApiResponse] = useState<GenerateSchemaResponseData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateSchema = async () => {
    setIsLoading(true);
    setError(null);
    setApiResponse(null);

    const payload: GenerateSchemaPayload = {
      input_data: "id,name,value\\n1,Test Item,10.99\\n2,Another Item,20.50",
      input_type: "csv",
      target_db: "mysql",
      source_name: "my_items.csv"
    };

    const result = await generateSchemaAPI(payload);

    if (result.error_message) {
      setError(result.error_message);
    } else {
      setApiResponse(result);
    }
    setIsLoading(false);
  };

  return (
    <div>
      <button onClick={handleGenerateSchema} disabled={isLoading}>
        {isLoading ? 'Generating Schema...' : 'Generate Schema'}
      </button>

      {isLoading && <p>Loading...</p>}

      {error && (
        <div style={{ color: 'red' }}>
          <h3>Error:</h3>
          <pre>{error}</pre>
        </div>
      )}

      {apiResponse && !apiResponse.error_message && (
        <div>
          <h3>API Response:</h3>
          {apiResponse.message && <p><strong>Message:</strong> {apiResponse.message}</p>}
          {apiResponse.output_ddl && (
            <div>
              <h4>Generated DDL:</h4>
              <pre>{apiResponse.output_ddl}</pre>
            </div>
          )}
          {apiResponse.schema_isr_data && (
             <div>
              <h4>Intermediate Schema (JSON):</h4>
              <pre>{JSON.stringify(apiResponse.schema_isr_data, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SchemaGeneratorComponent;
*/
