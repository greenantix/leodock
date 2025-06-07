"""
Context Indexing System
Vector database for semantic search and context management
Helps LEO quickly find relevant code, docs, and context
"""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging
import json
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class IndexedDocument:
    """Represents a document in the index"""
    id: str
    path: str
    content: str
    file_type: str
    last_modified: float
    metadata: Dict[str, Any]
    embedding_model: str


class ContextIndexer:
    """
    Manages vector database for semantic search of codebase
    Enables LEO to quickly find relevant context for supervision
    """
    
    def __init__(self, 
                 db_path: str = "./data/context_db",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 collection_name: str = "leodock_context"):
        
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model_name = embedding_model
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "LeoDock context and code indexing"}
        )
        
        # File type handlers
        self.file_handlers = {
            '.py': self._extract_python_context,
            '.js': self._extract_javascript_context,
            '.md': self._extract_markdown_context,
            '.txt': self._extract_text_context,
            '.json': self._extract_json_context,
            '.yaml': self._extract_yaml_context,
            '.yml': self._extract_yaml_context,
        }
        
        # Indexing patterns to include/exclude
        self.include_patterns = [
            '**/*.py',
            '**/*.js', 
            '**/*.md',
            '**/*.txt',
            '**/*.json',
            '**/*.yaml',
            '**/*.yml'
        ]
        
        self.exclude_patterns = [
            '__pycache__/**',
            '.git/**',
            'node_modules/**',
            '*.pyc',
            '.env*',
            'data/**/*.db',
            'data/**/*.sqlite*'
        ]

    def index_project(self, project_path: str) -> Dict[str, Any]:
        """
        Index entire project for context search
        
        Args:
            project_path: Root path of project to index
            
        Returns:
            Indexing statistics
        """
        project_path = Path(project_path)
        stats = {
            'files_processed': 0,
            'files_indexed': 0,
            'files_skipped': 0,
            'errors': 0,
            'total_documents': 0
        }
        
        logger.info(f"Starting project indexing: {project_path}")
        
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                stats['files_processed'] += 1
                
                try:
                    if self._should_index_file(file_path):
                        doc = self._process_file(file_path)
                        if doc:
                            self._index_document(doc)
                            stats['files_indexed'] += 1
                        else:
                            stats['files_skipped'] += 1
                    else:
                        stats['files_skipped'] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    stats['errors'] += 1
        
        stats['total_documents'] = self.collection.count()
        logger.info(f"Indexing complete: {stats}")
        
        return stats

    def _should_index_file(self, file_path: Path) -> bool:
        """Determine if file should be indexed"""
        # Check if file extension is supported
        if file_path.suffix not in self.file_handlers:
            return False
            
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if file_path.match(pattern):
                return False
                
        # Check file size (skip very large files)
        try:
            if file_path.stat().st_size > 1024 * 1024:  # 1MB limit
                return False
        except OSError:
            return False
            
        return True

    def _process_file(self, file_path: Path) -> Optional[IndexedDocument]:
        """Process a single file for indexing"""
        try:
            # Get file stats
            stat = file_path.stat()
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                    
            # Extract context using appropriate handler
            handler = self.file_handlers.get(file_path.suffix, self._extract_text_context)
            extracted_content, metadata = handler(content, file_path)
            
            # Create document ID
            doc_id = hashlib.md5(str(file_path).encode()).hexdigest()
            
            return IndexedDocument(
                id=doc_id,
                path=str(file_path),
                content=extracted_content,
                file_type=file_path.suffix,
                last_modified=stat.st_mtime,
                metadata=metadata,
                embedding_model=self.embedding_model_name
            )
            
        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")
            return None

    def _extract_python_context(self, content: str, file_path: Path) -> Tuple[str, Dict[str, Any]]:
        """Extract context from Python files"""
        import ast
        
        metadata = {
            'file_type': 'python',
            'classes': [],
            'functions': [],
            'imports': []
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    metadata['classes'].append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    metadata['functions'].append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        metadata['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    metadata['imports'].append(node.module)
                    
        except SyntaxError:
            # If parsing fails, just use raw content
            pass
            
        # Include docstrings and comments for better context
        context_content = content
        
        return context_content, metadata

    def _extract_javascript_context(self, content: str, file_path: Path) -> Tuple[str, Dict[str, Any]]:
        """Extract context from JavaScript files"""
        metadata = {
            'file_type': 'javascript',
            'functions': [],
            'classes': [],
            'exports': []
        }
        
        # Simple regex-based extraction (could be enhanced with proper JS parser)
        import re
        
        # Find function declarations
        func_matches = re.findall(r'function\s+(\w+)', content)
        metadata['functions'].extend(func_matches)
        
        # Find arrow functions
        arrow_matches = re.findall(r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>', content)
        metadata['functions'].extend(arrow_matches)
        
        # Find class declarations
        class_matches = re.findall(r'class\s+(\w+)', content)
        metadata['classes'].extend(class_matches)
        
        return content, metadata

    def _extract_markdown_context(self, content: str, file_path: Path) -> Tuple[str, Dict[str, Any]]:
        """Extract context from Markdown files"""
        import re
        
        metadata = {
            'file_type': 'markdown',
            'headings': [],
            'code_blocks': []
        }
        
        # Extract headings
        heading_matches = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        metadata['headings'] = [{'level': len(match[0]), 'text': match[1]} 
                               for match in heading_matches]
        
        # Extract code blocks
        code_matches = re.findall(r'```(\w+)?\n(.*?)\n```', content, re.DOTALL)
        metadata['code_blocks'] = [{'language': match[0] or 'text', 'code': match[1]} 
                                  for match in code_matches]
        
        return content, metadata

    def _extract_text_context(self, content: str, file_path: Path) -> Tuple[str, Dict[str, Any]]:
        """Extract context from plain text files"""
        metadata = {
            'file_type': 'text',
            'line_count': len(content.splitlines()),
            'word_count': len(content.split())
        }
        
        return content, metadata

    def _extract_json_context(self, content: str, file_path: Path) -> Tuple[str, Dict[str, Any]]:
        """Extract context from JSON files"""
        metadata = {
            'file_type': 'json',
            'keys': []
        }
        
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                metadata['keys'] = list(data.keys())
        except json.JSONDecodeError:
            pass
            
        return content, metadata

    def _extract_yaml_context(self, content: str, file_path: Path) -> Tuple[str, Dict[str, Any]]:
        """Extract context from YAML files"""
        metadata = {
            'file_type': 'yaml',
            'keys': []
        }
        
        try:
            import yaml
            data = yaml.safe_load(content)
            if isinstance(data, dict):
                metadata['keys'] = list(data.keys())
        except (ImportError, yaml.YAMLError):
            pass
            
        return content, metadata

    def _index_document(self, doc: IndexedDocument):
        """Add document to vector database"""
        # Generate embedding
        embedding = self.embedding_model.encode(doc.content).tolist()
        
        # Prepare metadata for ChromaDB
        chroma_metadata = {
            'path': doc.path,
            'file_type': doc.file_type,
            'last_modified': doc.last_modified,
            'embedding_model': doc.embedding_model,
            **doc.metadata
        }
        
        # Convert lists to strings for ChromaDB compatibility
        for key, value in chroma_metadata.items():
            if isinstance(value, list):
                chroma_metadata[key] = json.dumps(value)
        
        # Add to collection
        self.collection.add(
            ids=[doc.id],
            embeddings=[embedding],
            documents=[doc.content],
            metadatas=[chroma_metadata]
        )

    def search_context(self, 
                      query: str, 
                      n_results: int = 5,
                      file_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for relevant context using semantic similarity
        
        Args:
            query: Search query
            n_results: Number of results to return
            file_types: Filter by file types (e.g., ['.py', '.md'])
            
        Returns:
            List of matching documents with similarity scores
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Prepare where clause for filtering
        where_clause = {}
        if file_types:
            where_clause["file_type"] = {"$in": file_types}
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause if where_clause else None
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i].copy()
            
            # Parse JSON strings back to lists
            for key, value in metadata.items():
                if isinstance(value, str) and value.startswith('['):
                    try:
                        metadata[key] = json.loads(value)
                    except json.JSONDecodeError:
                        pass
            
            formatted_results.append({
                'id': results['ids'][0][i],
                'path': metadata['path'],
                'content': results['documents'][0][i],
                'distance': results['distances'][0][i],
                'metadata': metadata
            })
        
        return formatted_results

    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get indexed information for a specific file"""
        doc_id = hashlib.md5(file_path.encode()).hexdigest()
        
        try:
            result = self.collection.get(ids=[doc_id])
            if result['ids']:
                metadata = result['metadatas'][0].copy()
                
                # Parse JSON strings back to lists
                for key, value in metadata.items():
                    if isinstance(value, str) and value.startswith('['):
                        try:
                            metadata[key] = json.loads(value)
                        except json.JSONDecodeError:
                            pass
                
                return {
                    'id': result['ids'][0],
                    'content': result['documents'][0],
                    'metadata': metadata
                }
        except Exception as e:
            logger.error(f"Error retrieving file info for {file_path}: {e}")
            
        return None

    def update_file(self, file_path: str) -> bool:
        """Update a single file in the index"""
        try:
            path_obj = Path(file_path)
            if not path_obj.exists() or not self._should_index_file(path_obj):
                return False
                
            # Remove existing document
            doc_id = hashlib.md5(file_path.encode()).hexdigest()
            try:
                self.collection.delete(ids=[doc_id])
            except:
                pass  # Document might not exist
            
            # Add updated document
            doc = self._process_file(path_obj)
            if doc:
                self._index_document(doc)
                return True
                
        except Exception as e:
            logger.error(f"Error updating file {file_path}: {e}")
            
        return False

    def get_stats(self) -> Dict[str, Any]:
        """Get indexing statistics"""
        try:
            count = self.collection.count()
            
            # Get file type distribution
            all_results = self.collection.get()
            file_types = {}
            
            for metadata in all_results['metadatas']:
                file_type = metadata.get('file_type', 'unknown')
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            return {
                'total_documents': count,
                'file_type_distribution': file_types,
                'embedding_model': self.embedding_model_name,
                'db_path': str(self.db_path)
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'error': str(e)}