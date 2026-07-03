"""
Ensemble RAG System using LangChain and Hugging Face embeddings

Combines:
1. Dense Retrieval: Hugging Face sentence embeddings (semantic search)
2. Sparse Retrieval: BM25 (keyword search)
3. Ensemble: Weighted combination of both retrievers

References:
- LangChain EnsembleRetriever: https://python.langchain.com/docs/modules/data_connection/retrievers/ensemble
- Hugging Face embeddings: sentence-transformers/all-MiniLM-L6-v2
"""

import os
import json
from typing import List, Dict, Any, Optional, Union

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# EnsembleRetriever and BM25Retriever moved between langchain versions
EnsembleRetriever = None
for _path in ["langchain.retrievers", "langchain_community.retrievers", "langchain_classic.retrievers"]:
    try:
        _mod = __import__(_path, fromlist=["EnsembleRetriever"])
        EnsembleRetriever = _mod.EnsembleRetriever
        break
    except (ImportError, AttributeError):
        continue

BM25Retriever = None
for _path in ["langchain_community.retrievers", "langchain_classic.retrievers"]:
    try:
        _mod = __import__(_path, fromlist=["BM25Retriever"])
        BM25Retriever = _mod.BM25Retriever
        break
    except (ImportError, AttributeError):
        continue

from src.config import config


class EnsembleRAG:
    """
    Ensemble RAG system combining semantic and keyword search
    
    Architecture:
    1. Documents → Split into chunks
    2. Chunks → Two retrievers:
       a. Dense: FAISS + HuggingFace embeddings (semantic)
       b. Sparse: BM25 (keyword)
    3. Ensemble: Weighted combination
    """
    
    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        weights: List[float] = [0.5, 0.5],
        vector_store_path: Optional[str] = None
    ):
        """
        Initialize the Ensemble RAG system
        
        Args:
            embedding_model: Hugging Face model for embeddings
            chunk_size: Size of document chunks
            chunk_overlap: Overlap between chunks
            weights: [dense_weight, sparse_weight] for ensemble
            vector_store_path: Path to save/load FAISS index
        """
        self.embedding_model_name = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.weights = weights
        
        # Set vector store path
        if vector_store_path is None:
            self.vector_store_path = os.path.join(
                config.base_path, 
                "knowledge_base", 
                "vector_store"
            )
        else:
            self.vector_store_path = vector_store_path
        
        # Ensure directory exists
        os.makedirs(self.vector_store_path, exist_ok=True)
        
        # Initialize components
        self.embeddings = None
        self.vector_store = None
        self.dense_retriever = None
        self.sparse_retriever = None
        self.ensemble_retriever = None
        self.text_splitter = None
        
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize all components"""
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        print(f"✅ EnsembleRAG initialized with {self.embedding_model_name}")
        print(f"   Chunk size: {self.chunk_size}, Overlap: {self.chunk_overlap}")
        print(f"   Weights: dense={self.weights[0]}, sparse={self.weights[1]}")
    
    def load_documents_from_texts(self, texts: List[str], metadata: Optional[List[Dict]] = None) -> List[Document]:
        """
        Convert texts to LangChain Documents
        
        Args:
            texts: List of text strings
            metadata: Optional metadata for each document
        
        Returns:
            List of Document objects
        """
        documents = []
        for i, text in enumerate(texts):
            meta = metadata[i] if metadata else {"source": f"doc_{i}"}
            documents.append(Document(page_content=text, metadata=meta))
        return documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks
        
        Args:
            documents: List of Document objects
        
        Returns:
            List of chunked Documents
        """
        return self.text_splitter.split_documents(documents)
    
    def build_index(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Build the ensemble index from documents
        
        Args:
            documents: List of Document objects
        
        Returns:
            Dictionary with index status
        """
        print(f"📚 Building Ensemble RAG index from {len(documents)} documents...")
        
        # Chunk documents
        chunks = self.chunk_documents(documents)
        print(f"   Created {len(chunks)} chunks")
        
        # Extract text content for BM25
        chunk_texts = [chunk.page_content for chunk in chunks]
        
        # Build dense retriever (FAISS)
        print("   Building dense retriever (FAISS + HuggingFace embeddings)...")
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        self.dense_retriever = self.vector_store.as_retriever(
            search_kwargs={"k": 4}
        )
        
        # Build sparse retriever (BM25)
        print("   Building sparse retriever (BM25)...")
        self.sparse_retriever = BM25Retriever.from_texts(
            chunk_texts,
            metadatas=[chunk.metadata for chunk in chunks]
        )
        self.sparse_retriever.k = 4
        
        # Build ensemble retriever
        print("   Building ensemble retriever...")
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[self.dense_retriever, self.sparse_retriever],
            weights=self.weights
        )
        
        # Save vector store
        self._save_vector_store()
        
        print(f"✅ Ensemble RAG index built successfully!")
        return {
            "status": "success",
            "document_count": len(documents),
            "chunk_count": len(chunks),
            "dense_retriever": "FAISS + HuggingFace",
            "sparse_retriever": "BM25",
            "weights": self.weights
        }
    
    def _save_vector_store(self):
        """Save FAISS vector store to disk"""
        if self.vector_store:
            index_path = os.path.join(self.vector_store_path, "faiss_index")
            self.vector_store.save_local(index_path)
            print(f"   Vector store saved to: {index_path}")
    
    def load_vector_store(self) -> bool:
        """
        Load vector store from disk
        
        Returns:
            True if loaded successfully, False otherwise
        """
        index_path = os.path.join(self.vector_store_path, "faiss_index")
        
        if os.path.exists(index_path):
            try:
                self.vector_store = FAISS.load_local(
                    index_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                self.dense_retriever = self.vector_store.as_retriever(
                    search_kwargs={"k": 4}
                )
                
                # Rebuild BM25 from stored documents
                # Note: BM25 needs the original texts; we need to reload them
                print("✅ Vector store loaded successfully")
                return True
            except Exception as e:
                print(f"⚠️ Error loading vector store: {e}")
                return False
        else:
            print("⚠️ No vector store found. Build the index first.")
            return False
    
    def query(self, query_text: str, top_k: int = 4) -> Dict[str, Any]:
        """
        Query the ensemble RAG system
        
        Args:
            query_text: The query string
            top_k: Number of results to return
        
        Returns:
            Dictionary with retrieved documents and metadata
        """
        if not self.ensemble_retriever:
            print("⚠️ No retriever available. Build or load the index first.")
            return {"error": "No retriever available"}
        
        # Retrieve documents
        documents = self.ensemble_retriever.invoke(query_text)
        
        # Limit to top_k
        documents = documents[:top_k]
        
        return {
            "query": query_text,
            "results": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": doc.metadata.get("_score", "N/A")
                }
                for doc in documents
            ],
            "result_count": len(documents)
        }
    
    def query_with_context(self, query_text: str, top_k: int = 4) -> Dict[str, Any]:
        """
        Query the RAG system and format context for LLM
        
        Args:
            query_text: The query string
            top_k: Number of results to return
        
        Returns:
            Dictionary with context and raw results
        """
        results = self.query(query_text, top_k)
        
        if "error" in results:
            return results
        
        # Format context for LLM
        context_parts = []
        for i, doc in enumerate(results["results"]):
            context_parts.append(f"[{i+1}] {doc['content']}")
        
        context = "\n\n".join(context_parts)
        
        return {
            "query": query_text,
            "context": context,
            "source_count": len(results["results"]),
            "sources": results["results"]
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG system"""
        stats = {
            "embedding_model": self.embedding_model_name,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "weights": self.weights,
            "has_vector_store": self.vector_store is not None,
            "has_ensemble_retriever": self.ensemble_retriever is not None,
            "vector_store_path": self.vector_store_path
        }
        
        # Check if vector store exists on disk
        index_path = os.path.join(self.vector_store_path, "faiss_index")
        stats["index_exists_on_disk"] = os.path.exists(index_path)
        
        return stats


class HealthcareRAG(EnsembleRAG):
    """
    Specialized RAG for healthcare compliance and cybersecurity
    
    Pre-loaded with healthcare-specific knowledge for Med-Sec Audit Agent
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.compliance_knowledge = self._load_compliance_knowledge()
    
    def _load_compliance_knowledge(self) -> Dict[str, Any]:
        """Load healthcare compliance knowledge from documents"""
        # Sample healthcare knowledge
        # In production, this would load from PDFs in knowledge_base/documents/
        return {
            "hipaa_privacy": {
                "rule": "HIPAA Privacy Rule",
                "description": "Protects individually identifiable health information",
                "key_points": [
                    "Patient consent required for disclosure",
                    "Minimum necessary standard applies",
                    "Patients have right to access their records"
                ]
            },
            "hipaa_security": {
                "rule": "HIPAA Security Rule",
                "description": "Protects electronic protected health information (ePHI)",
                "key_points": [
                    "Administrative safeguards required",
                    "Physical safeguards for data centers",
                    "Technical safeguards including encryption"
                ]
            },
            "breach_notification": {
                "rule": "Breach Notification Rule",
                "description": "Required notification for breaches of unsecured PHI",
                "key_points": [
                    "Notify affected individuals within 60 days",
                    "Notify HHS for breaches affecting 500+ individuals",
                    "Media notification for large breaches"
                ]
            }
        }
    
    def query_compliance(self, topic: str) -> Dict[str, Any]:
        """
        Query compliance knowledge
        
        Args:
            topic: Compliance topic (e.g., "hipaa_privacy", "breach_notification")
        
        Returns:
            Compliance knowledge
        """
        if topic in self.compliance_knowledge:
            return {
                "status": "success",
                "topic": topic,
                "knowledge": self.compliance_knowledge[topic]
            }
        
        # Try semantic search as fallback
        query = f"HIPAA compliance: {topic}"
        rag_result = self.query_with_context(query)
        
        if rag_result.get("source_count", 0) > 0:
            return {
                "status": "success",
                "topic": topic,
                "source": "rag_search",
                "context": rag_result["context"]
            }
        
        return {
            "status": "error",
            "topic": topic,
            "message": "No compliance knowledge found for this topic"
        }
    
    def query_cybersecurity(self, topic: str) -> Dict[str, Any]:
        """
        Query cybersecurity knowledge
        
        Args:
            topic: Cybersecurity topic (e.g., "phishing", "ransomware")
        
        Returns:
            Cybersecurity knowledge
        """
        query = f"Healthcare cybersecurity: {topic}"
        return self.query_with_context(query)


def create_healthcare_rag(
    documents: Optional[List[Document]] = None,
    load_existing: bool = False,
    **kwargs
) -> HealthcareRAG:
    """
    Factory function to create and initialize a HealthcareRAG instance
    
    Args:
        documents: Optional list of documents to index
        load_existing: Whether to load existing index from disk
        **kwargs: Additional arguments for HealthcareRAG
    
    Returns:
        Initialized HealthcareRAG instance
    """
    rag = HealthcareRAG(**kwargs)
    
    if load_existing:
        rag.load_vector_store()
        print("✅ Loaded existing vector store")
    
    if documents:
        rag.build_index(documents)
    
    return rag


# Example usage
if __name__ == "__main__":
    # Test with sample documents
    sample_docs = [
        "HIPAA Privacy Rule protects patient health information. Patients have the right to access their records.",
        "HIPAA Security Rule requires administrative, physical, and technical safeguards for ePHI.",
        "Breach notification requires reporting breaches within 60 days.",
        "NIST Cybersecurity Framework provides guidelines for healthcare security.",
        "Multi-factor authentication is recommended for healthcare systems access."
    ]
    
    rag = create_healthcare_rag(
        documents=[Document(page_content=text) for text in sample_docs],
        chunk_size=200,
        chunk_overlap=20
    )
    
    # Test query
    result = rag.query_with_context("What are HIPAA requirements for patient data?")
    print("\n📋 Query Result:")
    print(f"Query: {result['query']}")
    print(f"Context: {result['context'][:200]}...")
    print(f"Sources: {result['source_count']}")