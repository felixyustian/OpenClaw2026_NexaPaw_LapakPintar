"""
tools/rag_db.py — ChromaDB-backed RAG store for sales history & business context.
"""

from __future__ import annotations

import json
import os
import uuid
from typing import Any

from loguru import logger

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False


class RAGDatabase:
    """Thin wrapper around ChromaDB for agent memory."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8001,
        collection_name: str = "umkm_memory",
    ):
        self.collection_name = collection_name
        self._client = None
        self._collection = None

        if CHROMA_AVAILABLE:
            try:
                self._client = chromadb.HttpClient(host=host, port=port)
                self._collection = self._client.get_or_create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"},
                )
                logger.info(f"[RAGDatabase] Connected to ChromaDB at {host}:{port}")
            except Exception as e:
                logger.warning(f"[RAGDatabase] ChromaDB unavailable: {e} — using in-memory fallback.")
                self._fallback: list[dict] = []
        else:
            logger.warning("[RAGDatabase] chromadb not installed — using in-memory fallback.")
            self._fallback: list[dict] = []

    def upsert(self, record: dict[str, Any]) -> None:
        doc_id = record.get("id") or str(uuid.uuid4())
        text = json.dumps(record, ensure_ascii=False)

        if self._collection:
            try:
                self._collection.upsert(ids=[doc_id], documents=[text])
                return
            except Exception as e:
                logger.error(f"[RAGDatabase] Upsert failed: {e}")

        # Fallback
        self._fallback.append({"id": doc_id, "text": text, "data": record})

    def query(self, query_text: str, top_k: int = 5) -> list[dict]:
        if self._collection:
            try:
                results = self._collection.query(
                    query_texts=[query_text], n_results=top_k
                )
                docs = results.get("documents", [[]])[0]
                return [json.loads(d) for d in docs]
            except Exception as e:
                logger.error(f"[RAGDatabase] Query failed: {e}")

        # Fallback: simple text search
        matched = [
            r["data"]
            for r in self._fallback
            if query_text.lower() in r["text"].lower()
        ]
        return matched[:top_k]

    def count(self) -> int:
        if self._collection:
            try:
                return self._collection.count()
            except Exception:
                pass
        return len(self._fallback)
