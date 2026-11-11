"""Local semantic search. Only model weights are cached; the index is in memory."""
from dataclasses import dataclass
from pathlib import Path

import numpy as np

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


@dataclass(frozen=True)
class Chunk:
    source: str
    number: int
    text: str


def load_chunks(directory: Path, size: int = 220, overlap: int = 40) -> list[Chunk]:
    if not 0 <= overlap < size:
        raise ValueError("Require 0 <= overlap < chunk size")
    chunks = []
    for path in sorted(directory.glob("*.md")):
        words = path.read_text(encoding="utf-8").split()
        for start in range(0, len(words), size - overlap):
            chunks.append(Chunk(path.name, start // (size - overlap) + 1,
                                " ".join(words[start:start + size])))
            if start + size >= len(words):
                break
    if not chunks:
        raise ValueError(f"No nonempty Markdown documents in {directory}")
    return chunks


def normalized(vectors):
    matrix = np.asarray(list(vectors), dtype=np.float32)
    return matrix / np.maximum(np.linalg.norm(matrix, axis=1, keepdims=True), 1e-12)


class SemanticIndex:
    def __init__(self, directory: Path, embedder=None):
        self.chunks = load_chunks(directory)
        if embedder is None:
            from fastembed import TextEmbedding
            embedder = TextEmbedding(model_name=EMBEDDING_MODEL,
                                     cache_dir=str(Path(__file__).parent / ".cache"),
                                     threads=2)
        self.embedder = embedder
        self.vectors = normalized(embedder.passage_embed(c.text for c in self.chunks))

    def search(self, query: str, k: int = 3) -> list[dict]:
        if not isinstance(query, str) or not query.strip() or len(query) > 1000:
            raise ValueError("Search query must contain 1–1000 characters")
        if type(k) is not int or not 1 <= k <= 5:
            raise ValueError("k must be an integer from 1 to 5")
        query_vector = normalized(self.embedder.query_embed(query))[0]
        scores = self.vectors @ query_vector
        results = []
        for position in np.argsort(-scores, kind="stable")[:k]:
            chunk = self.chunks[position]
            results.append({"source": f"{chunk.source}#chunk-{chunk.number}",
                            "score": round(float(scores[position]), 4), "text": chunk.text})
        return results
