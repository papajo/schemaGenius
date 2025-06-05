// frontend/src/App.tsx

import React from "react";
import InputPage from "./pages/InputPage"; // Import the InputPage component
import "./App.css"; // Keep existing App.css for any global styles

function App() {
  return (
    <div className="App">
      {/* You can add a header or layout components here if needed in the future */}
      {/* <header className="App-header">
        <h1>SchemaGenius</h1>
      </header> */}
      <main>
        <InputPage />
      </main>
    </div>
  );
}

export default App;
