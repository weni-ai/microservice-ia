from typing import Any, Iterable, List, Optional, Tuple
import unittest

from langchain.vectorstores import VectorStore
from langchain.docstore.document import Document
from app.store.elasticsearch_vector_store import ElasticsearchVectorStoreIndex

class ElasticsearchVectorStoreIndexTest(unittest.TestCase):
    def setUp(self):
        self.vectorstore = VectorStoreMock()
        self.storage = ElasticsearchVectorStoreIndex(self.vectorstore)

    def test_save(self):
        doc = Document(page_content="test doc", metadata={"id": "abc123"})
        self.storage.save(doc)
        assert len(self.vectorstore.storage) == 1

    def test_save_batch(self):
        documents = [
            Document(page_content="first doc", metadata={"id": "abc123"}),
            Document(page_content="second doc", metadata={"id": "Jane Doe"})
        ]
        self.storage.save_batch(documents)
        assert len(self.vectorstore.storage) == 2

    def test_search(self):
        self.vectorstore.add_texts(["test doc"], [{"id": "abc123"}])
        results = self.storage.search(search="test", filter={"id": "abc123"})
        assert len(results) == 1
        assert results[0][0].page_content == "test doc"

if __name__ == "__main__":
    unittest.main()

class VectorStoreMock(VectorStore):
    def __init__(self):
        self.storage = []
        
    def add_texts(self, texts: Iterable[str], metadatas: list[dict] | None = None, **kwargs: Any) -> List[str]:
        i = 0
        for text in texts:
            doc = Document(page_content=text, metadata=metadatas[i])
            self.storage.append(doc)
            i=i+1
            
        return texts
    
    def similarity_search(self, query: str, k: int = 4, **kwargs: Any) -> List[Document]:
        return super().similarity_search(query, k, **kwargs)
    
    def from_texts(
        self,
        texts,
        embedding,
        metadatas = None,
        **kwargs: Any,
    ):
        pass

    def similarity_search_with_score(
        self, query: str, k: int = 4, filter: Optional[dict] = None, **kwargs: Any
    ) -> List[Tuple[Document, float]]:
        
        matched_documents = [doc for doc in self.storage if query in doc.page_content.lower()]

        if filter is not None:
            matched_documents = self._apply_filter(matched_documents, filter)

        return [(td, 1.6) for td in matched_documents]

    def _apply_filter(self, documents: list[Document], filter: dict) -> list[Document]:
        filtered_documents = []
        for doc in documents:
            matched = all(doc.metadata.get(k) == v for k, v in filter.items())
            if matched:
                filtered_documents.append(doc)
        return filtered_documents
