import hashlib
from pathlib import Path

import chromadb
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from insightforge.config import Config

IGNORED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__"}


def build_index_id(folder_path: str) -> str:
    return hashlib.md5(folder_path.encode()).hexdigest()[:12]


def index_codebase(folder_path: str, config: Config | None = None) -> str:
    if config is None:
        config = Config()

    root = Path(folder_path)
    if not root.exists():
        return f"Folder không tồn tại: {folder_path}"

    # Load documents — bỏ qua các folder không cần thiết
    reader = SimpleDirectoryReader(
        input_dir=str(root),
        exclude_hidden=True,
        recursive=True,
        exclude=[str(root / d) for d in IGNORED_DIRS if (root / d).exists()],
    )
    documents = reader.load_data()
    if not documents:
        return "Không tìm thấy file nào để index."

    # Embedding với nomic-embed-text
    embed_model = OllamaEmbedding(
        model_name=config.embed_model,
        base_url=config.ollama_base_url,
        ollama_additional_kwargs={"keep_alive": config.embed_keep_alive},
    )

    # ChromaDB collection per folder
    collection_name = build_index_id(folder_path)
    chroma_client = chromadb.PersistentClient(path=str(config.chroma_dir))

    # reset nếu đã tồn tại (re-index)
    try:
        chroma_client.delete_collection(collection_name)
    except Exception:
        pass
    collection = chroma_client.create_collection(collection_name)

    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
    )

    return f"Index hoàn tất: {len(documents)} files → collection '{collection_name}'"
