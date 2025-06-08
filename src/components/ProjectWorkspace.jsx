import React, { useState } from 'react';
import { ArrowLeft, Database } from 'lucide-react';
import FileUploader from './FileUploader';
import CodeInput from './CodeInput';
import NaturalLanguageInput from './NaturalLanguageInput';

const ProjectWorkspace = ({ project, onBackToDashboard }) => {
  const [activeTab, setActiveTab] = useState('upload');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [analysisResults, setAnalysisResults] = useState(null);

  const tabs = [
    { id: 'upload', label: 'File Upload', icon: '📁' },
    { id: 'code', label: 'Code Input', icon: '💻' },
    { id: 'natural', label: 'Natural Language', icon: '💬' }
  ];

  const handleFileUpload = (files) => {
    setUploadedFiles(prev => [...prev, ...files]);
  };

  const handleAnalysis = (results) => {
    setAnalysisResults(results);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={onBackToDashboard}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
              >
                <ArrowLeft className="h-5 w-5 text-gray-600" />
              </button>
              <div className="flex items-center space-x-3">
                <div className="bg-primary-600 p-2 rounded-lg">
                  <Database className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-semibold text-gray-900">{project.name}</h1>
                  <p className="text-sm text-gray-600">Schema Design Project</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <span className="px-3 py-1 bg-primary-100 text-primary-800 text-sm font-medium rounded-full">
                {project.status === 'new' ? 'New Project' : project.status}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Input Section */}
          <div className="lg:col-span-2">
            <div className="card">
              {/* Tab Navigation */}
              <div className="border-b border-gray-200">
                <nav className="flex space-x-8 px-6">
                  {tabs.map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                        activeTab === tab.id
                          ? 'border-primary-500 text-primary-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                    >
                      <span className="mr-2">{tab.icon}</span>
                      {tab.label}
                    </button>
                  ))}
                </nav>
              </div>

              {/* Tab Content */}
              <div className="p-6">
                {activeTab === 'upload' && (
                  <FileUploader 
                    onFileUpload={handleFileUpload}
                    onAnalysis={handleAnalysis}
                  />
                )}
                {activeTab === 'code' && (
                  <CodeInput onAnalysis={handleAnalysis} />
                )}
                {activeTab === 'natural' && (
                  <NaturalLanguageInput onAnalysis={handleAnalysis} />
                )}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Project Info */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Information</h3>
              <div className="space-y-3">
                <div>
                  <label className="text-sm font-medium text-gray-700">Created</label>
                  <p className="text-sm text-gray-600">{project.createdAt.toLocaleDateString()}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">Last Modified</label>
                  <p className="text-sm text-gray-600">{project.lastModified.toLocaleDateString()}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">Status</label>
                  <p className="text-sm text-gray-600 capitalize">{project.status}</p>
                </div>
              </div>
            </div>

            {/* Uploaded Files */}
            {uploadedFiles.length > 0 && (
              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Uploaded Files</h3>
                <div className="space-y-2">
                  {uploadedFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{file.name}</p>
                        <p className="text-xs text-gray-600">{file.type} • {(file.size / 1024).toFixed(1)} KB</p>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        file.status === 'processed' 
                          ? 'bg-success-100 text-success-800'
                          : file.status === 'processing'
                          ? 'bg-warning-100 text-warning-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {file.status || 'uploaded'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Analysis Results Preview */}
            {analysisResults && (
              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Results</h3>
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Tables Detected</label>
                    <p className="text-sm text-gray-600">{analysisResults.tables?.length || 0}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Relationships</label>
                    <p className="text-sm text-gray-600">{analysisResults.relationships?.length || 0}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Confidence</label>
                    <p className="text-sm text-gray-600">{analysisResults.confidence || 'N/A'}%</p>
                  </div>
                </div>
                <button className="btn-primary w-full mt-4">
                  View Schema Editor
                </button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default ProjectWorkspace;