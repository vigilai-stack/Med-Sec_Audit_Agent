"""
RAG Knowledge Agent
Provides compliance and cybersecurity knowledge retrieval
"""

import os
import json
from typing import Dict, List, Any, Optional

from src.config import config
from src.rag_ensemble import HealthcareRAG
from src.rag_loader import RAGDocumentLoader


class RAGKnowledgeAgent:
    """
    RAG Agent that provides knowledge retrieval for compliance and cybersecurity
    
    This agent can:
    - Query the knowledge base for compliance rules
    - Retrieve cybersecurity best practices
    - Provide context for audit decisions
    - Answer regulatory questions
    """
    
    def __init__(self, auto_load: bool = True):
        self.knowledge_base_path = os.path.join(config.base_path, "knowledge_base")
        self.documents_path = os.path.join(self.knowledge_base_path, "documents")
        self.vector_store_path = os.path.join(self.knowledge_base_path, "vector_store")
        
        self.loader = None
        self.rag = None
        self.documents_loaded = False
        
        # Create directories if they don't exist
        os.makedirs(self.documents_path, exist_ok=True)
        os.makedirs(self.vector_store_path, exist_ok=True)
        
        if auto_load:
            self.initialize()
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize the RAG agent"""
        print("\n🧠 Initializing RAG Knowledge Agent...")
        
        # Initialize document loader
        self.loader = RAGDocumentLoader()
        
        # Try to load existing vector store
        self.rag = HealthcareRAG(
            vector_store_path=self.vector_store_path,
            chunk_size=1000,
            chunk_overlap=100
        )
        
        # Check if vector store exists
        index_path = os.path.join(self.vector_store_path, "faiss_index")
        
        if os.path.exists(index_path):
            print("   📂 Loading existing vector store...")
            success = self.rag.load_vector_store()
            if success:
                self.documents_loaded = True
                print("   ✅ RAG agent initialized with existing vector store")
                return {"status": "success", "mode": "existing"}
        
        # Check if there are documents to load
        if os.path.exists(self.documents_path) and os.listdir(self.documents_path):
            print("   📄 Loading documents from knowledge base...")
            return self.load_documents()
        
        print("   ⚠️ No documents found and no vector store exists.")
        print("   📝 RAG agent initialized in empty mode (no knowledge loaded)")
        return {"status": "warning", "mode": "empty", "message": "No documents or vector store found"}
    
    def load_documents(self) -> Dict[str, Any]:
        """Load and index documents from the knowledge base"""
        print("   📄 Loading documents...")
        
        # Load documents
        documents = self.loader.load_all_documents()
        
        if not documents:
            print("   ⚠️ No documents found in knowledge base")
            return {"status": "warning", "mode": "empty", "message": "No documents found"}
        
        # Build index
        print(f"   🏗️ Building RAG index from {len(documents)} documents...")
        result = self.rag.build_index(documents)
        self.documents_loaded = True
        
        print(f"   ✅ RAG agent initialized with {len(documents)} documents")
        return {
            "status": "success",
            "mode": "loaded",
            "document_count": len(documents),
            "result": result
        }

    def build_index(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """
        Build the FAISS index from documents in the knowledge base.

        Args:
            force_rebuild: If True, rebuild the index even if one already exists.

        Returns:
            Dictionary with index status and stats.
        """
        print("\n🏗️  Building FAISS index...")

        # Ensure loader is ready
        if self.loader is None:
            self.loader = RAGDocumentLoader()

        # Ensure rag engine is initialized (auto_load=False skips initialize())
        if self.rag is None:
            from src.rag_ensemble import HealthcareRAG
            self.rag = HealthcareRAG(
                vector_store_path=self.vector_store_path,
                chunk_size=1000,
                chunk_overlap=100
            )

        index_path = os.path.join(self.vector_store_path, "faiss_index")

        # If an index already exists and we're not forcing a rebuild, short-circuit.
        if os.path.exists(index_path) and not force_rebuild:
            print("   ℹ️  Index already exists. Loading it (use force_rebuild=True to rebuild).")
            success = self.rag.load_vector_store()
            if success:
                self.documents_loaded = True
                return {
                    "status": "success",
                    "mode": "existing",
                    "message": "Index already exists; loaded it."
                }
            # fall through to rebuild if loading failed
            print("   ⚠️  Existing index failed to load. Rebuilding...")

        # Load raw documents from disk
        documents = self.loader.load_all_documents()
        if not documents:
            print("   ⚠️  No documents found in knowledge_base/documents/")
            return {
                "status": "warning",
                "mode": "empty",
                "message": "No documents found in knowledge_base/documents/"
            }

        # Delegate to the underlying HealthcareRAG/EnsembleRAG build_index
        result = self.rag.build_index(documents)
        self.documents_loaded = True

        print("✅ FAISS index built and saved!")
        return {
            "status": "success",
            "mode": "built",
            "document_count": len(documents),
            "result": result
        }
    
    def query(self, question: str, top_k: int = 4) -> Dict[str, Any]:
        """
        Query the knowledge base
        
        Args:
            question: The question to ask
            top_k: Number of sources to retrieve
        
        Returns:
            Dictionary with answer and sources
        """
        if not self.documents_loaded:
            return {
                "status": "warning",
                "message": "No knowledge loaded. Please load documents first.",
                "answer": "I don't have any knowledge loaded yet. Please add documents to the knowledge base."
            }
        
        # Query RAG
        result = self.rag.query_with_context(question, top_k)
        
        if "error" in result:
            return {
                "status": "error",
                "message": result["error"]
            }
        
        return {
            "status": "success",
            "question": question,
            "context": result["context"],
            "sources": result["sources"],
            "source_count": result["source_count"]
        }
    
    def get_compliance_rules(self, regulation: str = "HIPAA") -> Dict[str, Any]:
        """Get compliance rules for a specific regulation"""
        return self.rag.query_compliance(regulation.lower().replace(" ", "_"))
    
    def get_cybersecurity_controls(self, framework: str = "NIST") -> Dict[str, Any]:
        """Get cybersecurity controls from a framework"""
        return self.rag.query_cybersecurity(framework)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG agent"""
        stats = {
            "documents_loaded": self.documents_loaded,
            "knowledge_base_path": self.knowledge_base_path,
            "documents_path": self.documents_path,
            "vector_store_path": self.vector_store_path
        }
        
        if self.rag:
            stats["rag_stats"] = self.rag.get_stats()
        
        return stats