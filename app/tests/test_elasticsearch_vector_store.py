import unittest

from langchain.vectorstores import ElasticVectorSearch
from langchain.docstore.document import Document
from app.store.elasticsearch_vector_store import ElasticsearchVectorStoreIndex, ContentBaseElasticsearchVectorStoreIndex
from unittest.mock import Mock


class ElasticsearchVectorStoreIndexTest(unittest.TestCase):
    def setUp(self):
        self.vectorstore = Mock(spec=ElasticVectorSearch)
        self.vectorstore.index_name = "index_test"
        self.vectorstore.client = Mock()
        self.vectorstore.client.indices = Mock()
        self.storage = ElasticsearchVectorStoreIndex(self.vectorstore)

    def test_save(self):
        self.vectorstore.add_texts.return_value = [
            "f40a4707-549e-4847-8f48-19b1987b8149"
        ]
        doc = Document(page_content="test doc", metadata={"doc_generic_id": "abc123"})
        result = self.storage.save(doc)
        self.vectorstore.add_texts.assert_called_once_with(
            [doc.page_content], [doc.metadata]
        )
        self.assertEqual(result, ["f40a4707-549e-4847-8f48-19b1987b8149"])

    def test_save_batch(self):
        docs_ids = [
            "1cdd36e4-8e4c-45b7-b3e4-e0365eee0b64",
            "8dce43f4-f20b-4035-b10d-f42476af4fb2",
        ]
        self.vectorstore.add_texts.return_value = docs_ids
        documents = [
            Document(page_content="first doc", metadata={"doc_generic_id": "abc123"}),
            Document(page_content="second doc", metadata={"doc_generic_id": "abc124"}),
        ]
        result = self.storage.save_batch(documents)
        self.vectorstore.add_texts.assert_called_once_with(
            [doc.page_content for doc in documents],
            [doc.metadata for doc in documents],
        )
        self.assertEqual(result, docs_ids)

    def test_search(self):
        self.vectorstore.similarity_search_with_score.return_value = [
            (
                Document(
                    page_content="test doc", metadata={"doc_generic_id": "abc123"}
                ),
                1.6,
            )
        ]
        results = self.storage.search(
            search="test", filter={"doc_generic_id": "abc123"}
        )
        self.vectorstore.similarity_search_with_score.assert_called_once_with(
            query="test", k=15, filter={"doc_generic_id": "abc123"}
        )
        self.assertEqual(1, len(results))
        self.assertEqual(results[0].page_content, "test doc")

    def test_delete(self):
        self.vectorstore.delete.return_value = True
        result = self.storage.delete(ids=["9ff6c70f-1dc4-4d52-b918-8d0d55462a45"])
        self.assertEqual(True, result)

    def test_query_search(self):
        self.vectorstore.client.indices.get.return_value = True
        mock_search_hits = [{"_id": "53899082-cf01-41d1-ba9b-320a90670755"}]
        self.vectorstore.client.search.return_value = {
            "hits": {"hits": mock_search_hits}
        }
        result = self.storage.query_search(
            {"doc_generic_id": "123", "metadata.sku": ["SKU-123"]}
        )
        self.assertEqual(result, mock_search_hits)

    def test_query_search_with_exception(self):
        self.vectorstore.client.indices.get.side_effect = RuntimeError(
            "Index Not Found"
        )
        result = self.storage.query_search(
            {"doc_generic_id": "123", "metadata.sku": ["SKU-123"]}
        )
        self.assertEqual(result, [])


class ContentBaseElasticsearchVectorStoreIndexTest(unittest.TestCase):
    def setUp(self):
        self.vectorstore = Mock(spec=ElasticVectorSearch)
        self.vectorstore.index_name = "index_test"
        self.vectorstore.client = Mock()
        self.vectorstore.embeddings = Mock()
        self.vectorstore.client.indices = Mock()
        self.storage = ContentBaseElasticsearchVectorStoreIndex(self.vectorstore)
        self.doc = Document(
            page_content="test doc",
            metadata={
                "full_page": "test document index",
                "content_base_uuid": "dfff32e7-dce6-40f7-a86e-8f9618887977"
            }
        )

    def test_save(self):
        self.vectorstore.from_documents.return_value = [
            "f40a4707-549e-4847-8f48-19b1987b8149"
        ]
        doc = Document(
            page_content="test doc",
            metadata={
                "full_page": "test document index",
                "content_base_uuid": "dfff32e7-dce6-40f7-a86e-8f9618887977"
            }
        )
        result = self.storage.save(doc)
        self.vectorstore.from_documents(
            [self.doc], self.vectorstore.embeddings, self.vectorstore.index_name
        )
        self.assertEqual(result, ["f40a4707-549e-4847-8f48-19b1987b8149"])

    def test_delete(self):
        self.vectorstore.delete.return_value = True
        result = self.storage.delete(ids=["dfff32e7-dce6-40f7-a86e-8f9618887977"])
        self.assertEqual(True, result)

    def test_search(self):
        self.vectorstore.similarity_search_with_score.return_value = [
            (
                self.doc,
                1.5,
            )
        ]
        query_filter = {"content_base_uuid": "dfff32e7-dce6-40f7-a86e-8f9618887977"}
        results = self.storage.search(
            search="test", filter=query_filter
        )
        self.vectorstore.similarity_search_with_score.assert_called_once_with(
            query="test", k=5, filter={"bool": {"filter": [{"term": {"metadata.content_base_uuid.keyword": "dfff32e7-dce6-40f7-a86e-8f9618887977"}}]}}
        )
        self.assertEqual(1, len(results))
        self.assertEqual(results[0].page_content, "test doc")

    def test_query_search(self):
        self.vectorstore.client.indices.get.return_value = True
        mock_search_hits = [{"_id": "53899082-cf01-41d1-ba9b-320a90670755"}]
        self.vectorstore.client.search.return_value = {
            "hits": {"hits": mock_search_hits}
        }
        result = self.storage.query_search(
            {"metadata.content_base_uuid": "dfff32e7-dce6-40f7-a86e-8f9618887977"}
        )
        self.assertEqual(result, mock_search_hits)

    def test_query_search_with_exception(self):
        query_filter = {"content_base_uuid": "dfff32e7-dce6-40f7-a86e-8f9618887977"}

        self.vectorstore.client.indices.get.side_effect = RuntimeError(
            "Index Not Found"
        )
        result = self.storage.query_search(
            query_filter
        )
        self.assertEqual(result, [])

    def test_search_delete(self):
        search_filter = {
            "metadata.content_base_uuid": "dfff32e7-dce6-40f7-a86e-8f9618887977",
            "metadata.filename": "filename.pdf"
        }
        self.vectorstore.client.indices.get.return_value = True
        self.vectorstore.client.search.return_value = {
            "_scroll_id": "dfff32e7",
            "hits": {
                "hits": [{"_id": "53899082-cf01-41d1-ba9b-320a90670755"}]
            }
        }
        result = self.storage.search_delete(search_filter)
        mock_search_tuple = ('dfff32e7', [{'_id': '53899082-cf01-41d1-ba9b-320a90670755'}])
        self.assertEqual(result, mock_search_tuple)

    def test_search_delete_scroll_id(self):
        search_filter = {
            "metadata.content_base_uuid": "dfff32e7-dce6-40f7-a86e-8f9618887977",
            "metadata.filename": "filename.pdf"
        }
        self.vectorstore.client.indices.get.return_value = True
        self.vectorstore.client.scroll.return_value = {
            "_scroll_id": "53899082",
            "hits": {
                "hits": [{"_id": "43899082-cf01-81d1-ba9b-329a90670755"}]
            }
        }
        result = self.storage.search_delete(search_filter, "dfff32e7")
        mock_search_tuple = ('53899082', [{'_id': '43899082-cf01-81d1-ba9b-329a90670755'}])
        self.assertEqual(result, mock_search_tuple)

    def test_search_delete_with_exception(self):
        search_filter = {
            "metadata.content_base_uuid": "dfff32e7-dce6-40f7-a86e-8f9618887977",
            "metadata.filename": "filename.pdf"
        }
        self.vectorstore.client.indices.get.side_effect = RuntimeError(
            "Index Not Found"
        )
        result = self.storage.search_delete(search_filter)
        self.assertEqual(result, [])
