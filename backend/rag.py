from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from backend.models import RetrievedContext
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
TOP_K = 4

_collection_cache = None


def _collection():
    global _collection_cache
    if _collection_cache is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        _collection_cache = client.get_collection("portfolio", embedding_function=ef)
    return _collection_cache


def retrieve(query: str, k: int = TOP_K) -> RetrievedContext:
    results = _collection().query(query_texts=[query], n_results=k)
    return RetrievedContext(query=query, chunks=results["documents"][0])
