import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from insightforge.config import Config
from insightforge.tools.indexer import build_index_id


def query_index(folder_path: str, query: str, config: Config | None = None) -> str:
    if config is None:
        config = Config()

    collection_name = build_index_id(folder_path)
    chroma_client = chromadb.PersistentClient(path=str(config.chroma_dir))

    try:
        collection = chroma_client.get_collection(collection_name)
    except Exception:
        return "Chưa có index cho folder này. Hãy chạy /index trước."

    embed_model = OllamaEmbedding(
        model_name=config.embed_model,
        base_url=config.ollama_base_url,
        ollama_additional_kwargs={"keep_alive": config.embed_keep_alive},
    )

    vector_store = ChromaVectorStore(chroma_collection=collection)
    index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
    retriever = index.as_retriever(similarity_top_k=5)
    nodes = retriever.retrieve(query)

    if not nodes:
        return "Không tìm thấy context liên quan."

    parts = []
    for i, node in enumerate(nodes, 1):
        source = node.metadata.get("file_name", "unknown")
        parts.append(f"[{i}] {source}\n{node.text[:500]}")
    return "\n\n".join(parts)
