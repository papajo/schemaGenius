import React, { useState } from 'react';
import { Code, Play, AlertCircle } from 'lucide-react';

const CodeInput = ({ onAnalysis }) => {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('sql');
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  const languages = [
    { id: 'sql', name: 'SQL DDL', example: 'CREATE TABLE users (\n  id INT PRIMARY KEY,\n  email VARCHAR(255) UNIQUE,\n  created_at TIMESTAMP\n);' },
    { id: 'python', name: 'Python SQLAlchemy', example: 'class User(db.Model):\n    id = db.Column(db.Integer, primary_key=True)\n    email = db.Column(db.String(255), unique=True)\n    created_at = db.Column(db.DateTime)' },
    { id: 'java', name: 'Java JPA', example: '@Entity\npublic class User {\n    @Id\n    private Long id;\n    \n    @Column(unique = true)\n    private String email;\n}' }
  ];

  const handleAnalyze = async () => {
    if (!code.trim()) {
      setError('Please enter some code to analyze');
      return;
    }

    setAnalyzing(true);
    setError(null);

    try {
      // Simulate analysis
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const analysis = analyzeCode(code, language);
      onAnalysis(analysis);
    } catch (err) {
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const analyzeCode = (code, language) => {
    switch (language) {
      case 'sql':
        return analyzeSQLCode(code);
      case 'python':
        return analyzePythonCode(code);
      case 'java':
        return analyzeJavaCode(code);
      default:
        throw new Error('Unsupported language');
    }
  };

  const analyzeSQLCode = (code) => {
    const tableMatches = code.match(/CREATE\s+TABLE\s+(\w+)\s*\(([\s\S]*?)\)/gi) || [];
    
    const tables = tableMatches.map(match => {
      const tableNameMatch = match.match(/CREATE\s+TABLE\s+(\w+)/i);
      const tableName = tableNameMatch ? tableNameMatch[1] : 'unknown_table';
      
      const columnSection = match.match(/\(([\s\S]*)\)/)[1];
      const columnLines = columnSection.split(',').map(line => line.trim()).filter(line => line);
      
      const columns = columnLines.map(line => {
        const parts = line.split(/\s+/);
        const name = parts[0];
        const type = parts[1] || 'VARCHAR';
        const isPrimaryKey = line.toUpperCase().includes('PRIMARY KEY');
        const isUnique = line.toUpperCase().includes('UNIQUE');
        const isNotNull = line.toUpperCase().includes('NOT NULL');
        
        return {
          name,
          type: type.toUpperCase(),
          nullable: !isNotNull && !isPrimaryKey,
          isPrimaryKey,
          isUnique,
          samples: []
        };
      });

      return {
        name: tableName,
        columns,
        rowCount: 0
      };
    });

    return {
      type: 'sql',
      tables,
      confidence: 95,
      relationships: extractSQLRelationships(code)
    };
  };

  const analyzePythonCode = (code) => {
    const classMatches = code.match(/class\s+(\w+)\s*\([^)]*\):/g) || [];
    
    const tables = classMatches.map(match => {
      const className = match.match(/class\s+(\w+)/)[1];
      const classBody = extractClassBody(code, className);
      
      const columnMatches = classBody.match(/(\w+)\s*=\s*db\.Column\([^)]*\)/g) || [];
      
      const columns = columnMatches.map(colMatch => {
        const name = colMatch.match(/(\w+)\s*=/)[1];
        const typeMatch = colMatch.match(/db\.(\w+)/);
        const type = typeMatch ? typeMatch[1].toUpperCase() : 'VARCHAR';
        const isPrimaryKey = colMatch.includes('primary_key=True');
        const isUnique = colMatch.includes('unique=True');
        const isNullable = !colMatch.includes('nullable=False') && !isPrimaryKey;
        
        return {
          name,
          type,
          nullable: isNullable,
          isPrimaryKey,
          isUnique,
          samples: []
        };
      });

      return {
        name: className.toLowerCase(),
        columns,
        rowCount: 0
      };
    });

    return {
      type: 'python',
      tables,
      confidence: 90,
      relationships: []
    };
  };

  const analyzeJavaCode = (code) => {
    const classMatches = code.match(/@Entity[\s\S]*?class\s+(\w+)/g) || [];
    
    const tables = classMatches.map(match => {
      const className = match.match(/class\s+(\w+)/)[1];
      const classBody = extractJavaClassBody(code, className);
      
      const fieldMatches = classBody.match(/private\s+\w+\s+\w+;/g) || [];
      
      const columns = fieldMatches.map(fieldMatch => {
        const parts = fieldMatch.replace('private', '').replace(';', '').trim().split(/\s+/);
        const type = parts[0];
        const name = parts[1];
        
        const fieldSection = extractFieldSection(classBody, name);
        const isPrimaryKey = fieldSection.includes('@Id');
        const isUnique = fieldSection.includes('unique = true');
        
        return {
          name,
          type: mapJavaType(type),
          nullable: !isPrimaryKey,
          isPrimaryKey,
          isUnique,
          samples: []
        };
      });

      return {
        name: className.toLowerCase(),
        columns,
        rowCount: 0
      };
    });

    return {
      type: 'java',
      tables,
      confidence: 88,
      relationships: []
    };
  };

  const extractClassBody = (code, className) => {
    const classStart = code.indexOf(`class ${className}`);
    if (classStart === -1) return '';
    
    let braceCount = 0;
    let start = -1;
    let end = -1;
    
    for (let i = classStart; i < code.length; i++) {
      if (code[i] === ':' && start === -1) {
        start = i + 1;
      }
      if (start !== -1) {
        if (code[i] === '{') braceCount++;
        if (code[i] === '}') braceCount--;
        if (braceCount === 0 && code[i] === '}') {
          end = i;
          break;
        }
      }
    }
    
    return start !== -1 && end !== -1 ? code.substring(start, end) : code.substring(classStart);
  };

  const extractJavaClassBody = (code, className) => {
    const classStart = code.indexOf(`class ${className}`);
    if (classStart === -1) return '';
    
    let braceCount = 0;
    let start = -1;
    
    for (let i = classStart; i < code.length; i++) {
      if (code[i] === '{') {
        if (start === -1) start = i + 1;
        braceCount++;
      }
      if (code[i] === '}') {
        braceCount--;
        if (braceCount === 0) {
          return code.substring(start, i);
        }
      }
    }
    
    return code.substring(classStart);
  };

  const extractFieldSection = (classBody, fieldName) => {
    const fieldIndex = classBody.indexOf(fieldName);
    if (fieldIndex === -1) return '';
    
    const beforeField = classBody.substring(0, fieldIndex);
    const lastAnnotation = Math.max(
      beforeField.lastIndexOf('@'),
      beforeField.lastIndexOf('\n')
    );
    
    return classBody.substring(lastAnnotation, fieldIndex + fieldName.length);
  };

  const mapJavaType = (javaType) => {
    const typeMap = {
      'String': 'VARCHAR',
      'Integer': 'INTEGER',
      'Long': 'BIGINT',
      'Double': 'DOUBLE',
      'Float': 'FLOAT',
      'Boolean': 'BOOLEAN',
      'Date': 'DATE',
      'LocalDateTime': 'TIMESTAMP'
    };
    return typeMap[javaType] || 'VARCHAR';
  };

  const extractSQLRelationships = (code) => {
    const foreignKeyMatches = code.match(/FOREIGN\s+KEY\s*\([^)]+\)\s*REFERENCES\s+(\w+)\s*\([^)]+\)/gi) || [];
    
    return foreignKeyMatches.map((match, index) => ({
      id: index,
      type: 'foreign_key',
      description: match.trim()
    }));
  };

  const setExample = (lang) => {
    const language = languages.find(l => l.id === lang);
    if (language) {
      setCode(language.example);
      setLanguage(lang);
    }
  };

  return (
    <div className="space-y-6">
      {/* Language Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Select Programming Language
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {languages.map((lang) => (
            <button
              key={lang.id}
              onClick={() => setExample(lang.id)}
              className={`p-4 text-left border rounded-lg transition-colors duration-200 ${
                language === lang.id
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-gray-200 hover:border-gray-300 text-gray-700'
              }`}
            >
              <div className="font-medium">{lang.name}</div>
              <div className="text-sm text-gray-600 mt-1">
                Click to load example
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Code Input */}
      <div>
        <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-2">
          Code Input
        </label>
        <div className="relative">
          <textarea
            id="code"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder={`Paste your ${languages.find(l => l.id === language)?.name || 'code'} here...`}
            className="w-full h-64 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm resize-none"
          />
          <div className="absolute top-3 right-3">
            <Code className="h-5 w-5 text-gray-400" />
          </div>
        </div>
        <div className="mt-2 text-sm text-gray-600">
          Supports SQL DDL, Python SQLAlchemy/Django ORM, and Java JPA annotations
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-error-50 border border-error-200 rounded-lg p-4 flex items-start space-x-3">
          <AlertCircle className="h-5 w-5 text-error-600 flex-shrink-0 mt-0.5" />
          <div>
            <div className="text-sm font-medium text-error-800">Analysis Error</div>
            <div className="text-sm text-error-700 mt-1">{error}</div>
          </div>
        </div>
      )}

      {/* Analyze Button */}
      <div className="flex justify-end">
        <button
          onClick={handleAnalyze}
          disabled={analyzing || !code.trim()}
          className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {analyzing ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Play className="h-4 w-4" />
              <span>Analyze Code</span>
            </>
          )}
        </button>
      </div>

      {/* Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-sm font-medium text-blue-800 mb-2">Tips for better analysis:</h4>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Include complete table definitions with column types and constraints</li>
          <li>• For ORM code, include relationship definitions when possible</li>
          <li>• Use standard naming conventions for better recognition</li>
          <li>• Include primary key and foreign key definitions</li>
        </ul>
      </div>
    </div>
  );
};

export default CodeInput;