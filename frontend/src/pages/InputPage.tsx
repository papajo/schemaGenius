// frontend/src/pages/InputPage.tsx

import React, { useState, FormEvent } from "react";
import { generateSchemaAPI, GenerateSchemaPayload, GenerateSchemaResponseData } from "../services/api";
// import './InputPage.css'; // Optional: Create and import a CSS file for styling

const InputPage: React.FC = () => {
  const [inputData, setInputData] = useState<string>("");
  const [inputType, setInputType] = useState<string>("json"); // Default input type
  const [targetDb, setTargetDb] = useState<string>("mysql");   // Default target DB
  const [sourceName, setSourceName] = useState<string>("");   // For CSV table name or other source hints

  const [apiResponse, setApiResponse] = useState<GenerateSchemaResponseData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    setApiResponse(null); // Clear previous response

    const payload: GenerateSchemaPayload = {
      input_data: inputData,
      input_type: inputType,
      target_db: targetDb || undefined,
      source_name: sourceName || undefined,
    };

    const result = await generateSchemaAPI(payload);
    setApiResponse(result);
    setIsLoading(false);
  };

  // Basic inline styling for simplicity in this scaffold.
  const styles: {[key: string]: React.CSSProperties} = {
    container: { padding: "20px", maxWidth: "800px", margin: "0 auto", fontFamily: "Arial, sans-serif", lineHeight: "1.6" },
    formGroup: { marginBottom: "20px" },
    label: { display: "block", marginBottom: "8px", fontWeight: "bold", fontSize: "14px" },
    input: { width: "100%", padding: "10px", boxSizing: "border-box", border: "1px solid #ccc", borderRadius: "4px", fontSize: "14px" },
    textarea: { width: "100%", minHeight: "200px", padding: "10px", boxSizing: "border-box", border: "1px solid #ccc", borderRadius: "4px", fontFamily: "monospace", fontSize: "14px" },
    select: { width: "100%", padding: "10px", boxSizing: "border-box", border: "1px solid #ccc", borderRadius: "4px", fontSize: "14px", backgroundColor: "white" },
    button: { padding: "12px 25px", backgroundColor: "#007bff", color: "white", border: "none", borderRadius: "4px", cursor: "pointer", fontSize: "16px", fontWeight: "bold" },
    buttonDisabled: { backgroundColor: "#cccccc", cursor: "not-allowed"},
    outputArea: { marginTop: "25px", padding: "15px", border: "1px solid #ddd", backgroundColor: "#f9f9f9", minHeight: "150px", whiteSpace: "pre-wrap", fontFamily: "monospace", borderRadius: "4px", overflowX: "auto", fontSize: "13px" },
    errorArea: { marginTop: "20px", padding: "10px 15px", border: "1px solid #dc3545", backgroundColor: "#f8d7da", color: "#721c24", borderRadius: "4px", whiteSpace: "pre-wrap" },
    infoArea: { marginTop: "20px", padding: "10px 15px", border: "1px solid #17a2b8", backgroundColor: "#d1ecf1", color: "#0c5460", borderRadius: "4px", whiteSpace: "pre-wrap" }
  };

  const displayMessage = apiResponse?.message && (!apiResponse.error_message || (apiResponse.output_ddl && apiResponse.message !== apiResponse.error_message));
  const displayError = apiResponse?.error_message;

  return (
    <div style={styles.container}>
      <header style={{textAlign: "center", marginBottom: "30px"}}>
        <h1>SchemaGenius</h1>
        <p style={{fontSize: "1.1em", color: "#555"}}>
          Intelligently generate database schemas from your code, text, or data.
        </p>
      </header>

      <form onSubmit={handleSubmit}>
        <div style={styles.formGroup}>
          <label htmlFor="inputData" style={styles.label}>Input Data:</label>
          <textarea
            id="inputData"
            value={inputData}
            onChange={(e) => setInputData(e.target.value)}
            required
            style={styles.textarea}
            placeholder="Paste your JSON, SQL DDL, CSV data, or Python ORM code here..."
          />
        </div>

        <div style={styles.formGroup}>
          <label htmlFor="inputType" style={styles.label}>Input Type:</label>
          <select id="inputType" value={inputType} onChange={(e) => setInputType(e.target.value)} style={styles.select}>
            <option value="json">JSON</option>
            <option value="sql">SQL DDL</option>
            <option value="csv">CSV</option>
            <option value="python">Python ORM (SQLAlchemy)</option>
            {/* <option value="text">Natural Language (Text)</option> Future option */}
          </select>
        </div>

        <div style={styles.formGroup}>
          <label htmlFor="sourceName" style={styles.label}>Source Name (Optional):</label>
          <input
            type="text"
            id="sourceName"
            value={sourceName}
            onChange={(e) => setSourceName(e.target.value)}
            style={styles.input}
            placeholder="e.g., my_data.csv (for CSV table name), or leave blank"
          />
        </div>

        <div style={styles.formGroup}>
          <label htmlFor="targetDb" style={styles.label}>Target Database (for DDL Generation):</label>
          <select id="targetDb" value={targetDb} onChange={(e) => setTargetDb(e.target.value)} style={styles.select}>
            <option value="mysql">MySQL</option>
            <option value="postgresql">PostgreSQL</option>
            <option value="">None (Process input only)</option>
          </select>
        </div>

        <button type="submit" disabled={isLoading} style={isLoading ? {...styles.button, ...styles.buttonDisabled} : styles.button}>
          {isLoading ? "Generating..." : "Generate Schema"}
        </button>
      </form>

      {isLoading && <p style={{textAlign: "center", marginTop: "20px"}}>Processing...</p>}

      {displayError && (
        <div style={styles.errorArea}>
            <strong>Error:</strong> {apiResponse?.error_message}
        </div>
      )}

      {displayMessage && (
         <div style={styles.infoArea}>
            <strong>Info:</strong> {apiResponse?.message}
        </div>
      )}

      {apiResponse?.output_ddl && (
        <div style={styles.outputArea}>
          <h3 style={{marginTop: 0}}>Generated DDL ({apiResponse.target_db || "N/A"}):</h3>
          <pre>{apiResponse.output_ddl}</pre>
        </div>
      )}
    </div>
  );
};

export default InputPage;
