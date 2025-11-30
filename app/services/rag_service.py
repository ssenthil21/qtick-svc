import os
from typing import List

class SimpleRAGService:
    def __init__(self, file_path: str = "data/qtick_info.txt"):
        self.chunks = []
        self._load_data(file_path)

    def _load_data(self, file_path: str):
        if not os.path.exists(file_path):
            print(f"Warning: Knowledge base file not found at {file_path}")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Split by double newlines to get paragraphs/sections
        raw_chunks = content.split("\n\n")
        self.chunks = [chunk.strip() for chunk in raw_chunks if chunk.strip()]

    def retrieve(self, query: str, top_k: int = 2) -> str:
        """
        Simple keyword-based retrieval.
        Returns the top_k chunks that share the most words with the query.
        """
        query_words = set(query.lower().split())
        if not query_words:
            return ""

        scored_chunks = []
        for chunk in self.chunks:
            chunk_words = set(chunk.lower().split())
            # Calculate overlap score
            score = len(query_words.intersection(chunk_words))
            if score > 0:
                scored_chunks.append((score, chunk))
        
        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        # Return top_k chunks joined
        top_chunks = [chunk for score, chunk in scored_chunks[:top_k]]
        return "\n\n".join(top_chunks)
