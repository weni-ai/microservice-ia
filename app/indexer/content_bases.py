from langchain.docstore.document import Document

from app.handlers.products import Product
from app.indexer import IDocumentIndexer
from app.store import IStorage
from typing import List
from uuid import UUID


class ContentBaseIndexer(IDocumentIndexer):
    def __init__(self, storage: IStorage):
        self.storage = storage

    def index_documents(self, docs: List[Document]):
        file_uuid = docs[0].metadata["file_uuid"]
        content_base_uuid = docs[0].metadata["content_base_uuid"]

        results = self._search_docs_by_content_base_uuid(
            content_base_uuid=content_base_uuid,
            file_uuid=file_uuid,
        )
        ids = []
        if len(results) > 0:
            ids = [item["_id"] for item in results]
            self.storage.delete(ids=ids)

        return self.storage.save(docs)

    def index(self, texts: List, metadatas: dict):
        results = self._search_docs_by_content_base_uuid(
            content_base_uuid=metadatas.get('content_base_uuid')
        )
        ids = []
        if len(results) > 0:
            ids = [item["_id"] for item in results]
            self.storage.delete(ids=ids)

        docs = [
            Document(page_content=text.lower(), metadata=metadatas)
            for text in texts
        ]

        return self.storage.save(docs)

    def index_batch(self):
        raise NotImplementedError

    def search(self, search, filter=None, threshold=0.1) -> list[Product]:
        matched_responses = self.storage.search(search, filter, threshold)
        return set([doc.metadata.get("full_page") for doc in matched_responses])

    def _search_docs_by_content_base_uuid(self, content_base_uuid: UUID, file_uuid: str = None):
        search_filter = {
            "metadata.content_base_uuid": content_base_uuid
        }
        if file_uuid:
            search_filter.update({"metadata.file_uuid": file_uuid})
        return self.storage.query_search(search_filter)

    def delete(self, content_base_uuid: UUID, filename: str, file_uuid: str):
        search_filter = {
            "metadata.content_base_uuid": content_base_uuid,
            "metadata.file_uuid": file_uuid,
        }

        if filename:
            search_filter.update({"metadata.source": filename})

        scroll_id, results = self.storage.search_delete(search_filter)
        ids = []

        while len(results) > 0:
            ids += [item["_id"] for item in results]
            scroll_id, results = self.storage.search_delete(search_filter, scroll_id)
        
        if ids:
            self.storage.delete(ids=ids)

    def delete_batch(self):
        raise NotImplementedError
