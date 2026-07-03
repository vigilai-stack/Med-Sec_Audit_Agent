# Hybrid RAG + Web Search
# Falls back to web search when RAG retrieval returns insufficient results

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# ── RAG components ─────────────────────────────────────────────────────────────
from src.rag_ensemble import EnsembleRAG, HealthcareRAG

# ── Web search (choose one) ────────────────────────────────────────────────────
# Option A: DuckDuckGo (free, no API key)
from langchain_community.tools import DuckDuckGoSearchRun

# Option B: Tavily (better quality, needs API key)
# from langchain_community.tools import TavilySearchResults

# Option C: SerpAPI (Google, needs API key)
# from langchain_community.utilities import SerpAPIWrapper


@dataclass
class RetrievalResult:
    """Unified result from either RAG or web search"""
    source: str           # "rag" | "web"
    content: str
    metadata: Dict[str, Any]
    confidence: float     # 0-relevance score (RAG) or heuristic (web)


class HybridRAG:
    """
    Hybrid retriever: tries RAG first, falls back to web search if needed.
    
    Flow:
    1. Query RAG ensemble (FAISS + BM25)
    2. If results meet confidence threshold → return RAG results
    3. Else → query web search
    4. Fuse / rerank combined results
    5. Return best-k with source attribution
    """

    def __init__(
        self,
        rag: EnsembleRAG,
        confidence_threshold: float = 0.5,
        min_rag_results: int = 2,
        web_top_k: int = 5,
        rerank: bool = True,
    ):
        self.rag = rag
        self.confidence_threshold = confidence_threshold
        self.min_rag_results = min_rag_results
        self.web_top_k = web_top_k
        self.rerank = rerank

        # Web search tool (DuckDuckGo = free, no key)
        self.web_search = DuckDuckGoSearchRun()
        # self.web_search = TavilySearchResults(max_results=web_top_k)  # if you have key

    def _rag_retrieve(self, query: str, top_k: int) -> List[RetrievalResult]:
        """Query RAG ensemble, return normalized results"""
        rag_result = self.rag.query(query, top_k=top_k)

        if "error" in rag_result:
            return []

        results = []
        for doc in rag_result.get("results", []):
            # Score heuristic: FAISS/BM25 don't return scores directly via invoke()
            # If using .get_relevant_documents() with scores, extract them
            results.append(RetrievalResult(
                source="rag",
                content=doc["content"],
                metadata=doc["metadata"],
                confidence=doc.get("score", 0.7)  # default medium confidence
            ))
        return results

    def _web_search(self, query: str) -> List[RetrievalResult]:
        """Query web search, return normalized results"""
        try:
            # DuckDuckGo returns a string summary; Tavily/SerpAPI return structured results
            raw = self.web_search.invoke(query)

            # Parse based on tool output format
            if isinstance(raw, str):
                # DuckDuckGo: single string summary
                return [RetrievalResult(
                    source="web",
                    content=raw,
                    metadata={"tool": "duckduckgo", "query": query},
                    confidence=0.6
                )]
            elif isinstance(raw, list):
                # Tavily/SerpAPI: list of dicts with title, snippet, url
                return [RetrievalResult(
                    source="web",
                    content=f"{r.get('title', '')}: {r.get('snippet', '')}",
                    metadata={"url": r.get("url", ""), "tool": "tavily"},
                    confidence=0.65
                ) for r in raw[:self.web_top_k]]
        except Exception as e:
            print(f"⚠️ Web search failed: {e}")
        return []

    def _rerank(self, query: str, results: List[RetrievalResult]) -> List[RetrievalResult]:
        """Optional: rerank combined results with cross-encoder"""
        if not self.rerank or len(results) <= 1:
            return results

        try:
            from sentence_transformers import CrossEncoder
            reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

            pairs = [(query, r.content) for r in results]
            scores = reranker.predict(pairs)

            for r, s in zip(results, scores):
                r.confidence = float(s)

            results.sort(key=lambda x: x.confidence, reverse=True)
        except ImportError:
            pass  # reranker not installed, skip
        return results

    def retrieve(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        """
        Main entry point: hybrid retrieval with source attribution.
        
        Returns:
            {
                "query": str,
                "results": [RetrievalResult...],
                "primary_source": "rag" | "web" | "hybrid",
                "rag_used": bool,
                "web_used": bool,
            }
        """
        # 1. Try RAG first
        rag_results = self._rag_retrieve(query, top_k * 2)

        # 2. Check if RAG results are sufficient
        high_conf_rag = [r for r in rag_results if r.confidence >= self.confidence_threshold]

        if len(high_conf_rag) >= self.min_rag_results:
            # RAG is sufficient
            final = self._rerank(query, high_conf_rag)[:top_k]
            return {
                "query": query,
                "results": final,
                "primary_source": "rag",
                "rag_used": True,
                "web_used": False,
            }

        # 3. Fallback to web search
        web_results = self._web_search(query)

        # 4. Combine and rerank
        combined = rag_results + web_results
        final = self._rerank(query, combined)[:top_k]

        primary = "hybrid" if rag_results and web_results else ("web" if web_results else "rag")

        return {
            "query": query,
            "results": final,
            "primary_source": primary,
            "rag_used": bool(rag_results),
            "web_used": bool(web_results),
        }

    def retrieve_with_context(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        """Format for LLM consumption with citations"""
        retrieval = self.retrieve(query, top_k)

        context_parts = []
        citations = []

        for i, r in enumerate(retrieval["results"]):
            marker = f"[{i+1}]"
            source_tag = "RAG" if r.source == "rag" else "WEB"
            context_parts.append(f"{marker} ({source_tag}) {r.content}")
            citations.append({
                "id": i + 1,
                "source": r.source,
                "content_preview": r.content[:200],
                "metadata": r.metadata,
                "confidence": r.confidence,
            })

        return {
            "query": query,
            "context": "\n\n".join(context_parts),
            "citations": citations,
            "primary_source": retrieval["primary_source"],
            "rag_used": retrieval["rag_used"],
            "web_used": retrieval["web_used"],
        }


# ── Convenience factory ────────────────────────────────────────────────────────

def create_hybrid_rag(
    vector_store_path: str = "./medsec_sandbox/vector_store",
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    **kwargs
) -> HybridRAG:
    """Create hybrid RAG with default HealthcareRAG backend"""
    rag = HealthcareRAG(
        vector_store_path=vector_store_path,
        embedding_model_name=embedding_model,
    )
    # Load existing index if available
    rag.load_vector_store()
    return HybridRAG(rag, **kwargs)


# ── Usage example ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    hybrid = create_hybrid_rag()

    # Test queries
    queries = [
        "HIPAA encryption requirements for PHI at rest",
        "CVE-2024-3094 xz backdoor details",          # likely not in RAG
        "NIST 800-53 AC-2 account management",        # may be in RAG
        "Latest ransomware trends 2024 healthcare",   # needs web
    ]

    for q in queries:
        print(f"\n{'='*60}")
        print(f"Query: {q}")
        result = hybrid.retrieve_with_context(q, top_k=3)
        print(f"Source: {result['primary_source']} (RAG: {result['rag_used']}, Web: {result['web_used']})")
        print(f"Context:\n{result['context'][:500]}...")
        print(f"Citations: {len(result['citations'])}")