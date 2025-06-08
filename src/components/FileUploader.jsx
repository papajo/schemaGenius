import React, { useState, useCallback } from 'react';
import { Upload, File, X, CheckCircle, AlertCircle, Loader } from 'lucide-react';

const FileUploader = ({ onFileUpload, onAnalysis }) => {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState([]);
  const [processing, setProcessing] = useState(false);

  const supportedFormats = [
    { type: 'CSV', description: 'Comma-separated values', extensions: ['.csv'] },
    { type: 'JSON', description: 'JavaScript Object Notation', extensions: ['.json'] },
    { type: 'XML', description: 'Extensible Markup Language', extensions: ['.xml'] },
    { type: 'TXT', description: 'Plain text files', extensions: ['.txt'] },
    { type: 'SQL', description: 'SQL script files', extensions: ['.sql'] },
    { type: 'TSV', description: 'Tab-separated values', extensions: ['.tsv'] }
  ];

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  }, []);

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(Array.from(e.target.files));
    }
  };

  const handleFiles = (newFiles) => {
    const processedFiles = newFiles.map(file => ({
      id: Date.now() + Math.random(),
      file,
      name: file.name,
      size: file.size,
      type: file.type || getFileType(file.name),
      status: 'uploaded',
      preview: null,
      analysis: null
    }));

    setFiles(prev => [...prev, ...processedFiles]);
    onFileUpload(processedFiles);
    
    // Start processing files
    processedFiles.forEach(processFile);
  };

  const getFileType = (filename) => {
    const extension = filename.split('.').pop()?.toLowerCase();
    const typeMap = {
      'csv': 'text/csv',
      'json': 'application/json',
      'xml': 'application/xml',
      'txt': 'text/plain',
      'sql': 'application/sql',
      'tsv': 'text/tab-separated-values'
    };
    return typeMap[extension] || 'application/octet-stream';
  };

  const processFile = async (fileData) => {
    setFiles(prev => prev.map(f => 
      f.id === fileData.id ? { ...f, status: 'processing' } : f
    ));

    try {
      const content = await readFileContent(fileData.file);
      const analysis = await analyzeFileContent(content, fileData.type, fileData.name);
      
      setFiles(prev => prev.map(f => 
        f.id === fileData.id 
          ? { ...f, status: 'processed', preview: content.substring(0, 500), analysis }
          : f
      ));

      // Trigger analysis callback with results
      if (analysis) {
        onAnalysis(analysis);
      }
    } catch (error) {
      console.error('Error processing file:', error);
      setFiles(prev => prev.map(f => 
        f.id === fileData.id 
          ? { ...f, status: 'error', error: error.message }
          : f
      ));
    }
  };

  const readFileContent = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = (e) => reject(new Error('Failed to read file'));
      reader.readAsText(file);
    });
  };

  const analyzeFileContent = async (content, fileType, filename) => {
    // Simulate analysis delay
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

    try {
      if (fileType.includes('csv') || filename.endsWith('.csv')) {
        return analyzeCSV(content);
      } else if (fileType.includes('json') || filename.endsWith('.json')) {
        return analyzeJSON(content);
      } else if (fileType.includes('xml') || filename.endsWith('.xml')) {
        return analyzeXML(content);
      } else if (fileType.includes('sql') || filename.endsWith('.sql')) {
        return analyzeSQL(content);
      } else {
        return analyzeText(content);
      }
    } catch (error) {
      throw new Error(`Analysis failed: ${error.message}`);
    }
  };

  const analyzeCSV = (content) => {
    const lines = content.split('\n').filter(line => line.trim());
    if (lines.length === 0) throw new Error('Empty CSV file');

    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    const sampleRows = lines.slice(1, Math.min(6, lines.length));
    
    const columns = headers.map(header => {
      const sampleValues = sampleRows.map(row => {
        const values = row.split(',');
        const index = headers.indexOf(header);
        return values[index]?.trim().replace(/"/g, '') || '';
      }).filter(v => v);

      return {
        name: header,
        type: inferDataType(sampleValues),
        nullable: sampleValues.some(v => !v),
        samples: sampleValues.slice(0, 3)
      };
    });

    return {
      type: 'csv',
      tables: [{
        name: 'imported_data',
        columns,
        rowCount: lines.length - 1
      }],
      confidence: 85,
      relationships: []
    };
  };

  const analyzeJSON = (content) => {
    const data = JSON.parse(content);
    
    if (Array.isArray(data)) {
      if (data.length === 0) throw new Error('Empty JSON array');
      
      const sample = data[0];
      const columns = Object.keys(sample).map(key => ({
        name: key,
        type: inferDataType([sample[key]]),
        nullable: data.some(item => item[key] == null),
        samples: data.slice(0, 3).map(item => item[key]).filter(v => v != null)
      }));

      return {
        type: 'json',
        tables: [{
          name: 'json_data',
          columns,
          rowCount: data.length
        }],
        confidence: 90,
        relationships: []
      };
    } else {
      // Single object - analyze structure
      const columns = Object.keys(data).map(key => ({
        name: key,
        type: inferDataType([data[key]]),
        nullable: data[key] == null,
        samples: [data[key]].filter(v => v != null)
      }));

      return {
        type: 'json',
        tables: [{
          name: 'json_object',
          columns,
          rowCount: 1
        }],
        confidence: 80,
        relationships: []
      };
    }
  };

  const analyzeXML = (content) => {
    // Basic XML analysis - in a real implementation, you'd use xml2js
    const elementMatches = content.match(/<(\w+)[^>]*>/g) || [];
    const elements = [...new Set(elementMatches.map(match => 
      match.replace(/<(\w+)[^>]*>/, '$1')
    ))];

    return {
      type: 'xml',
      tables: elements.map(element => ({
        name: element,
        columns: [
          { name: 'id', type: 'INTEGER', nullable: false, samples: [] },
          { name: 'content', type: 'TEXT', nullable: true, samples: [] }
        ],
        rowCount: (content.match(new RegExp(`<${element}`, 'g')) || []).length
      })),
      confidence: 70,
      relationships: []
    };
  };

  const analyzeSQL = (content) => {
    const createTableMatches = content.match(/CREATE\s+TABLE\s+(\w+)/gi) || [];
    const tables = createTableMatches.map(match => {
      const tableName = match.replace(/CREATE\s+TABLE\s+/i, '');
      return {
        name: tableName,
        columns: [
          { name: 'detected_column', type: 'VARCHAR', nullable: true, samples: [] }
        ],
        rowCount: 0
      };
    });

    return {
      type: 'sql',
      tables,
      confidence: 95,
      relationships: []
    };
  };

  const analyzeText = (content) => {
    const lines = content.split('\n').filter(line => line.trim());
    const words = content.split(/\s+/).filter(word => word.length > 2);
    
    return {
      type: 'text',
      tables: [{
        name: 'text_analysis',
        columns: [
          { name: 'line_number', type: 'INTEGER', nullable: false, samples: ['1', '2', '3'] },
          { name: 'content', type: 'TEXT', nullable: true, samples: lines.slice(0, 3) }
        ],
        rowCount: lines.length
      }],
      confidence: 60,
      relationships: []
    };
  };

  const inferDataType = (values) => {
    if (values.length === 0) return 'TEXT';
    
    const nonEmptyValues = values.filter(v => v !== '' && v != null);
    if (nonEmptyValues.length === 0) return 'TEXT';

    // Check if all values are integers
    if (nonEmptyValues.every(v => /^-?\d+$/.test(v))) {
      return 'INTEGER';
    }

    // Check if all values are floats
    if (nonEmptyValues.every(v => /^-?\d*\.?\d+$/.test(v))) {
      return 'DECIMAL';
    }

    // Check if all values are booleans
    if (nonEmptyValues.every(v => /^(true|false|yes|no|1|0)$/i.test(v))) {
      return 'BOOLEAN';
    }

    // Check if all values are dates
    if (nonEmptyValues.every(v => !isNaN(Date.parse(v)))) {
      return 'DATE';
    }

    return 'VARCHAR';
  };

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'processing':
        return <Loader className="h-4 w-4 text-warning-600 animate-spin" />;
      case 'processed':
        return <CheckCircle className="h-4 w-4 text-success-600" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-error-600" />;
      default:
        return <File className="h-4 w-4 text-gray-600" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div
        className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-colors duration-200 ${
          dragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          multiple
          onChange={handleFileInput}
          accept=".csv,.json,.xml,.txt,.sql,.tsv"
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        
        <div className="space-y-4">
          <div className="mx-auto w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
            <Upload className="h-8 w-8 text-primary-600" />
          </div>
          
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Upload your data files
            </h3>
            <p className="text-gray-600 mb-4">
              Drag and drop files here, or click to browse
            </p>
            <button className="btn-primary">
              Choose Files
            </button>
          </div>
        </div>
      </div>

      {/* Supported Formats */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {supportedFormats.map((format) => (
          <div key={format.type} className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="font-medium text-gray-900 mb-1">{format.type}</div>
            <div className="text-sm text-gray-600 mb-2">{format.description}</div>
            <div className="text-xs text-gray-500">
              {format.extensions.join(', ')}
            </div>
          </div>
        ))}
      </div>

      {/* Uploaded Files */}
      {files.length > 0 && (
        <div className="space-y-4">
          <h4 className="text-lg font-semibold text-gray-900">Uploaded Files</h4>
          <div className="space-y-3">
            {files.map((file) => (
              <div key={file.id} className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(file.status)}
                    <div>
                      <div className="font-medium text-gray-900">{file.name}</div>
                      <div className="text-sm text-gray-600">
                        {(file.size / 1024).toFixed(1)} KB • {file.type}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      file.status === 'processed' 
                        ? 'bg-success-100 text-success-800'
                        : file.status === 'processing'
                        ? 'bg-warning-100 text-warning-800'
                        : file.status === 'error'
                        ? 'bg-error-100 text-error-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {file.status}
                    </span>
                    <button
                      onClick={() => removeFile(file.id)}
                      className="p-1 hover:bg-gray-100 rounded transition-colors duration-200"
                    >
                      <X className="h-4 w-4 text-gray-500" />
                    </button>
                  </div>
                </div>

                {file.status === 'error' && (
                  <div className="bg-error-50 border border-error-200 rounded-lg p-3 mb-3">
                    <div className="text-sm text-error-800">{file.error}</div>
                  </div>
                )}

                {file.analysis && (
                  <div className="bg-gray-50 rounded-lg p-3 space-y-2">
                    <div className="text-sm font-medium text-gray-900">Analysis Results:</div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Tables:</span>
                        <span className="ml-1 font-medium">{file.analysis.tables?.length || 0}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Confidence:</span>
                        <span className="ml-1 font-medium">{file.analysis.confidence}%</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Type:</span>
                        <span className="ml-1 font-medium uppercase">{file.analysis.type}</span>
                      </div>
                    </div>
                    
                    {file.analysis.tables && file.analysis.tables.length > 0 && (
                      <div className="mt-3">
                        <div className="text-sm font-medium text-gray-900 mb-2">Detected Columns:</div>
                        <div className="flex flex-wrap gap-2">
                          {file.analysis.tables[0].columns.slice(0, 6).map((column, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-1 bg-primary-100 text-primary-800 text-xs rounded-full"
                            >
                              {column.name} ({column.type})
                            </span>
                          ))}
                          {file.analysis.tables[0].columns.length > 6 && (
                            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                              +{file.analysis.tables[0].columns.length - 6} more
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {file.preview && file.status === 'processed' && (
                  <details className="mt-3">
                    <summary className="text-sm font-medium text-gray-700 cursor-pointer hover:text-gray-900">
                      Preview Content
                    </summary>
                    <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                      <pre className="text-xs text-gray-600 whitespace-pre-wrap overflow-hidden">
                        {file.preview}
                        {file.preview.length >= 500 && '...'}
                      </pre>
                    </div>
                  </details>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Processing Indicator */}
      {processing && (
        <div className="text-center py-4">
          <Loader className="h-6 w-6 text-primary-600 animate-spin mx-auto mb-2" />
          <p className="text-sm text-gray-600">Processing files...</p>
        </div>
      )}
    </div>
  );
};

export default FileUploader;