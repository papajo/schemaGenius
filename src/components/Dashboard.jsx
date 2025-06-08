import React, { useState } from 'react';
import { Plus, Database, Clock, Search } from 'lucide-react';

const Dashboard = ({ onCreateProject }) => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [projectName, setProjectName] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  // Mock existing projects
  const existingProjects = [
    {
      id: '1',
      name: 'E-commerce Database',
      lastModified: new Date(Date.now() - 86400000), // 1 day ago
      status: 'completed'
    },
    {
      id: '2',
      name: 'User Management System',
      lastModified: new Date(Date.now() - 172800000), // 2 days ago
      status: 'in-progress'
    }
  ];

  const handleCreateProject = () => {
    if (projectName.trim()) {
      onCreateProject(projectName.trim());
      setProjectName('');
      setShowCreateModal(false);
    }
  };

  const filteredProjects = existingProjects.filter(project =>
    project.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-primary-600 p-2 rounded-lg">
                <Database className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">SchemaGenius</h1>
                <p className="text-sm text-gray-600">Database Schema Generator</p>
              </div>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-primary flex items-center space-x-2"
            >
              <Plus className="h-5 w-5" />
              <span>New Project</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Transform Your Data Into Perfect Schemas
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Upload your data files, code snippets, or describe your requirements in natural language. 
            SchemaGenius will analyze and generate optimized database schemas for any platform.
          </p>
        </div>

        {/* Quick Start */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="card p-6 text-center hover:shadow-md transition-shadow duration-200">
            <div className="bg-primary-100 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Database className="h-6 w-6 text-primary-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Upload Data Files</h3>
            <p className="text-gray-600">CSV, JSON, XML, or text files to automatically infer schema structure</p>
          </div>
          
          <div className="card p-6 text-center hover:shadow-md transition-shadow duration-200">
            <div className="bg-success-100 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Plus className="h-6 w-6 text-success-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Code Analysis</h3>
            <p className="text-gray-600">Paste SQL, Python ORM, or Java JPA code for instant schema extraction</p>
          </div>
          
          <div className="card p-6 text-center hover:shadow-md transition-shadow duration-200">
            <div className="bg-warning-100 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Clock className="h-6 w-6 text-warning-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Natural Language</h3>
            <p className="text-gray-600">Describe your database requirements and let AI generate the schema</p>
          </div>
        </div>

        {/* Projects Section */}
        {existingProjects.length > 0 && (
          <div className="card p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-900">Recent Projects</h3>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search projects..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>
            
            <div className="grid gap-4">
              {filteredProjects.map((project) => (
                <div
                  key={project.id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200 cursor-pointer"
                >
                  <div className="flex items-center space-x-4">
                    <div className="bg-primary-100 p-2 rounded-lg">
                      <Database className="h-5 w-5 text-primary-600" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">{project.name}</h4>
                      <p className="text-sm text-gray-600">
                        Last modified {project.lastModified.toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      project.status === 'completed' 
                        ? 'bg-success-100 text-success-800'
                        : 'bg-warning-100 text-warning-800'
                    }`}>
                      {project.status === 'completed' ? 'Completed' : 'In Progress'}
                    </span>
                    <button className="btn-secondary text-sm">Open</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md mx-4 animate-slide-up">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Create New Project</h3>
            <div className="mb-4">
              <label htmlFor="projectName" className="block text-sm font-medium text-gray-700 mb-2">
                Project Name
              </label>
              <input
                type="text"
                id="projectName"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="Enter project name..."
                className="input-field"
                onKeyPress={(e) => e.key === 'Enter' && handleCreateProject()}
                autoFocus
              />
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => setShowCreateModal(false)}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateProject}
                disabled={!projectName.trim()}
                className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Create Project
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;