from langchain.vectorstores import VectorStore
from langchain.docstore.document import Document

from app.store import IStorage


class ElasticsearchVectorStoreIndexGPT(IStorage):
    def __init__(self, vectorstore: VectorStore, score=1.55):
        self.vectorstore = vectorstore
        self.score = score

    def save(self, doc: Document) -> list[str]:
        raise NotImplementedError()

    def save_batch(self, documents: list[Document]) -> list[str]:
        raise NotImplementedError()

    def search(self, search: str, filter=None, threshold=1.6) -> list[Document]:
        # def search_on_elasticsearch(query, k=5, threshold=1.6):
        docs = self.vectorstore.similarity_search_with_score(search, k=5)
        return [{"body": doc[0].page_content} for doc in docs if doc[1] > threshold]

    def query_search(self, search_filter: dict) -> list[dict]:
        raise NotImplementedError()

    def delete(self, ids: list[str] = []) -> bool:
        raise NotImplementedError()
