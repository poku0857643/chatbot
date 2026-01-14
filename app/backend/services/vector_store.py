import faiss
import numpy as np
from typing import List, Tuple, Dict
from app.middleware.settings.settings import config


class VectorStore:
    """
    FAISS-based vector store for document retrieval.
    Stores document embeddings and metadata for RAG.
    """

    def __init__(self, dimension: int = None):
        """
        Initialize FAISS vector store.

        Args:
            dimension: Dimension of embedding vectors (default from config)
        """
        self.dimension = dimension or config.EMBEDDING_DIMENSION
        # L2 distance index for similarity search
        self.index = faiss.IndexFlatL2(self.dimension)
        # Store metadata: {index: {"text": chunk_text, "file_id": file_id, "filename": filename}}
        self.metadata: Dict[int, Dict[str, str]] = {}
        self.current_index = 0

    def add_documents(
        self,
        embeddings: List[List[float]],
        chunks: List[str],
        file_id: str,
        filename: str
    ) -> int:
        """
        Add document chunks to the vector store.

        Args:
            embeddings: List of embedding vectors
            chunks: List of text chunks corresponding to embeddings
            file_id: Unique file identifier
            filename: Original filename

        Returns:
            Number of chunks added
        """
        if len(embeddings) != len(chunks):
            raise ValueError("Number of embeddings must match number of chunks")

        if not embeddings:
            return 0

        # Convert to numpy array
        embeddings_array = np.array(embeddings, dtype=np.float32)

        # Add to FAISS index
        self.index.add(embeddings_array)

        # Store metadata
        for i, chunk in enumerate(chunks):
            self.metadata[self.current_index + i] = {
                "text": chunk,
                "file_id": file_id,
                "filename": filename
            }

        self.current_index += len(chunks)

        return len(chunks)

    def search(
        self,
        query_embedding: List[float],
        k: int = None
    ) -> List[Tuple[str, float, str]]:
        """
        Search for similar documents.

        Args:
            query_embedding: Query embedding vector
            k: Number of results to return (default from config)

        Returns:
            List of tuples: (chunk_text, distance, filename)
        """
        if self.index.ntotal == 0:
            return []

        k = k or config.TOP_K_RESULTS
        k = min(k, self.index.ntotal)  # Don't request more than available

        # Convert to numpy array
        query_array = np.array([query_embedding], dtype=np.float32)

        # Search
        distances, indices = self.index.search(query_array, k)

        # Retrieve results with metadata
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx in self.metadata:
                metadata = self.metadata[idx]
                results.append((
                    metadata["text"],
                    float(distance),
                    metadata["filename"]
                ))

        return results

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the vector store."""
        unique_files = len(set(m["file_id"] for m in self.metadata.values()))
        return {
            "total_chunks": self.index.ntotal,
            "unique_files": unique_files,
            "dimension": self.dimension
        }

    def clear(self):
        """Clear all data from the vector store."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = {}
        self.current_index = 0


# Global singleton instance
vector_store = VectorStore()
