from langchain.vectorstores import VectorStore
from langchain.docstore.document import Document
from app.store.interface import IStorage

class ElasticsearchVectorStoreIndex(IStorage):
    def __init__(self, vectorstore: VectorStore, score=1.55):
        self.vectorstore = vectorstore
        self.score = score

    def save(self, doc: Document):
        texts = [doc.page_content] 
        metadatas = [doc.metadata]
        return self.vectorstore.add_texts(texts, metadatas)

    def save_batch(self, documents: list[Document]):
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return self.vectorstore.add_texts(texts, metadatas)

    def search(self, search: str, filter=None, threshold=0.1) -> list[Document]:
        sr = self.vectorstore.similarity_search_with_score(query=search, k=15, filter=filter)
        return [doc[0] for doc in sr if doc[1] > threshold]
