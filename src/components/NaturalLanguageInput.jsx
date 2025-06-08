import React, { useState } from 'react';
import { MessageSquare, Sparkles, AlertCircle, Lightbulb } from 'lucide-react';

const NaturalLanguageInput = ({ onAnalysis }) => {
  const [description, setDescription] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  const examples = [
    {
      title: "E-commerce System",
      description: "I need a database for an online store. There should be a Users table with id, email, password, and created_at. A Products table with id, name, description, price, and stock_quantity. An Orders table with id, user_id, order_date, and total_amount. Each order belongs to a user, and users can have many orders."
    },
    {
      title: "Blog Platform",
      description: "Create a blog database with Users (id, username, email, password), Posts (id, title, content, author_id, published_at), and Comments (id, post_id, author_id, content, created_at). Users can write many posts and comments. Posts can have many comments."
    },
    {
      title: "Library Management",
      description: "Design a library system with Books (id, title, author, isbn, publication_year), Members (id, name, email, membership_date), and Borrowings (id, book_id, member_id, borrowed_date, return_date). Members can borrow multiple books, and books can be borrowed by different members over time."
    }
  ];

  const handleAnalyze = async () => {
    if (!description.trim()) {
      setError('Please enter a description to analyze');
      return;
    }

    setAnalyzing(true);
    setError(null);

    try {
      // Simulate NLP analysis
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      const analysis = analyzeNaturalLanguage(description);
      onAnalysis(analysis);
    } catch (err) {
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const analyzeNaturalLanguage = (text) => {
    // Simple NLP simulation - in reality, this would use advanced NLP models
    const entities = extractEntities(text);
    const relationships = extractRelationships(text);
    
    const tables = entities.map(entity => ({
      name: entity.name,
      columns: entity.attributes.map(attr => ({
        name: attr.name,
        type: inferTypeFromName(attr.name),
        nullable: !attr.required,
        isPrimaryKey: attr.name === 'id',
        isUnique: attr.name === 'email' || attr.name === 'username',
        samples: []
      })),
      rowCount: 0
    }));

    return {
      type: 'natural_language',
      tables,
      confidence: calculateConfidence(text, entities),
      relationships: relationships,
      ambiguities: findAmbiguities(text)
    };
  };

  const extractEntities = (text) => {
    const entities = [];
    
    // Look for table mentions
    const tablePatterns = [
      /(\w+)\s+table/gi,
      /table\s+(\w+)/gi,
      /(\w+)\s+\(/gi
    ];

    const foundTables = new Set();
    
    tablePatterns.forEach(pattern => {
      const matches = text.matchAll(pattern);
      for (const match of matches) {
        foundTables.add(match[1].toLowerCase());
      }
    });

    // Extract attributes for each table
    foundTables.forEach(tableName => {
      const attributes = extractAttributesForTable(text, tableName);
      entities.push({
        name: tableName,
        attributes: attributes
      });
    });

    return entities;
  };

  const extractAttributesForTable = (text, tableName) => {
    const attributes = [];
    
    // Look for attribute patterns
    const tableSection = extractTableSection(text, tableName);
    
    // Common attribute patterns
    const attributePatterns = [
      /(\w+),/g,
      /(\w+)\s+and/g,
      /(\w+)$/g,
      /(\w+)\./g
    ];

    const foundAttributes = new Set();
    
    attributePatterns.forEach(pattern => {
      const matches = tableSection.matchAll(pattern);
      for (const match of matches) {
        const attr = match[1].toLowerCase();
        if (attr.length > 1 && !isCommonWord(attr)) {
          foundAttributes.add(attr);
        }
      }
    });

    // Always add id if not present
    if (!foundAttributes.has('id')) {
      foundAttributes.add('id');
    }

    foundAttributes.forEach(attr => {
      attributes.push({
        name: attr,
        required: attr === 'id' || isRequiredField(attr)
      });
    });

    return attributes;
  };

  const extractTableSection = (text, tableName) => {
    const tableIndex = text.toLowerCase().indexOf(tableName);
    if (tableIndex === -1) return text;
    
    // Extract the sentence or paragraph containing the table
    const start = Math.max(0, text.lastIndexOf('.', tableIndex));
    const end = text.indexOf('.', tableIndex + tableName.length);
    
    return text.substring(start, end === -1 ? text.length : end);
  };

  const extractRelationships = (text) => {
    const relationships = [];
    
    // Look for relationship keywords
    const relationshipPatterns = [
      /(\w+)\s+belongs?\s+to\s+(\w+)/gi,
      /(\w+)\s+has\s+many\s+(\w+)/gi,
      /(\w+)\s+can\s+have\s+many\s+(\w+)/gi,
      /each\s+(\w+)\s+belongs?\s+to\s+(\w+)/gi
    ];

    relationshipPatterns.forEach(pattern => {
      const matches = text.matchAll(pattern);
      for (const match of matches) {
        relationships.push({
          from: match[1].toLowerCase(),
          to: match[2].toLowerCase(),
          type: determineRelationshipType(match[0])
        });
      }
    });

    return relationships;
  };

  const determineRelationshipType = (relationshipText) => {
    if (relationshipText.includes('belongs to')) {
      return 'many-to-one';
    } else if (relationshipText.includes('has many') || relationshipText.includes('can have many')) {
      return 'one-to-many';
    }
    return 'unknown';
  };

  const inferTypeFromName = (name) => {
    const typeMap = {
      'id': 'INTEGER',
      'email': 'VARCHAR',
      'password': 'VARCHAR',
      'name': 'VARCHAR',
      'title': 'VARCHAR',
      'description': 'TEXT',
      'content': 'TEXT',
      'price': 'DECIMAL',
      'amount': 'DECIMAL',
      'quantity': 'INTEGER',
      'count': 'INTEGER',
      'date': 'DATE',
      'created_at': 'TIMESTAMP',
      'updated_at': 'TIMESTAMP',
      'published_at': 'TIMESTAMP',
      'is_active': 'BOOLEAN',
      'is_published': 'BOOLEAN'
    };

    // Check exact matches first
    if (typeMap[name]) {
      return typeMap[name];
    }

    // Check patterns
    if (name.includes('_id') || name.endsWith('id')) {
      return 'INTEGER';
    }
    if (name.includes('_at') || name.includes('date')) {
      return 'TIMESTAMP';
    }
    if (name.includes('is_') || name.startsWith('has_')) {
      return 'BOOLEAN';
    }
    if (name.includes('price') || name.includes('amount') || name.includes('cost')) {
      return 'DECIMAL';
    }
    if (name.includes('count') || name.includes('quantity') || name.includes('number')) {
      return 'INTEGER';
    }

    return 'VARCHAR';
  };

  const isCommonWord = (word) => {
    const commonWords = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'table', 'database', 'system'];
    return commonWords.includes(word.toLowerCase());
  };

  const isRequiredField = (field) => {
    const requiredFields = ['id', 'email', 'name', 'title'];
    return requiredFields.includes(field);
  };

  const calculateConfidence = (text, entities) => {
    let confidence = 60; // Base confidence
    
    // Increase confidence for clear structure
    if (entities.length > 0) confidence += 10;
    if (text.includes('table')) confidence += 10;
    if (text.includes('belongs to') || text.includes('has many')) confidence += 10;
    if (text.includes('id')) confidence += 5;
    
    // Decrease confidence for vague language
    if (text.includes('maybe') || text.includes('possibly')) confidence -= 10;
    if (text.length < 50) confidence -= 15;
    
    return Math.min(95, Math.max(30, confidence));
  };

  const findAmbiguities = (text) => {
    const ambiguities = [];
    
    // Check for vague terms
    const vagueTerms = ['details', 'information', 'data', 'stuff', 'things'];
    vagueTerms.forEach(term => {
      if (text.toLowerCase().includes(term)) {
        ambiguities.push(`The term "${term}" is vague. Please specify what specific fields you need.`);
      }
    });

    return ambiguities;
  };

  const loadExample = (example) => {
    setDescription(example.description);
  };

  return (
    <div className="space-y-6">
      {/* Examples */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Quick Start Examples
        </label>
        <div className="grid gap-3">
          {examples.map((example, index) => (
            <button
              key={index}
              onClick={() => loadExample(example)}
              className="text-left p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors duration-200"
            >
              <div className="font-medium text-gray-900 mb-1">{example.title}</div>
              <div className="text-sm text-gray-600 line-clamp-2">
                {example.description.substring(0, 120)}...
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Description Input */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
          Describe Your Database Requirements
        </label>
        <div className="relative">
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe your database structure in plain English. For example: 'I need a user management system with users, roles, and permissions. Users have an id, email, password, and created date. Each user can have multiple roles...'"
            className="w-full h-48 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
          />
          <div className="absolute top-3 right-3">
            <MessageSquare className="h-5 w-5 text-gray-400" />
          </div>
        </div>
        <div className="mt-2 text-sm text-gray-600">
          Be specific about table names, field names, and relationships between entities
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
          disabled={analyzing || !description.trim()}
          className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {analyzing ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4" />
              <span>Analyze Description</span>
            </>
          )}
        </button>
      </div>

      {/* Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <Lightbulb className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-blue-800 mb-2">Tips for better analysis:</h4>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Clearly name your tables (e.g., "Users table", "Products table")</li>
              <li>• List specific field names for each table</li>
              <li>• Describe relationships using phrases like "belongs to", "has many"</li>
              <li>• Mention data types when known (e.g., "price as decimal", "date field")</li>
              <li>• Be specific rather than vague (avoid terms like "details" or "information")</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NaturalLanguageInput;