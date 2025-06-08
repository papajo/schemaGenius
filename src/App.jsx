import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import ProjectWorkspace from './components/ProjectWorkspace';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [currentProject, setCurrentProject] = useState(null);

  const handleCreateProject = (projectName) => {
    const newProject = {
      id: Date.now().toString(),
      name: projectName,
      createdAt: new Date(),
      lastModified: new Date(),
      status: 'new'
    };
    setCurrentProject(newProject);
    setCurrentView('project');
  };

  const handleBackToDashboard = () => {
    setCurrentView('dashboard');
    setCurrentProject(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {currentView === 'dashboard' ? (
        <Dashboard onCreateProject={handleCreateProject} />
      ) : (
        <ProjectWorkspace 
          project={currentProject} 
          onBackToDashboard={handleBackToDashboard}
        />
      )}
    </div>
  );
}

export default App;