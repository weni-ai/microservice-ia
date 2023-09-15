import unittest
from unittest.mock import Mock
from langchain.docstore.document import Document
from app.store.interface import IStorage
from app.indexer.products import ProductsIndexer
from app.handlers.products import Product

class TestProductsIndexer(unittest.TestCase):
    def setUp(self):
        self.mock_storage = Mock(spec=IStorage)
        self.indexer = ProductsIndexer(self.mock_storage)

    def test_index(self):
        mock_product = Product(
            id="1",
            title="Test Product",
            org_id="123",
            channel_id="456",
            catalog_id="789",
            product_retailer_id="999"
        )
        mock_document = Document(
            page_content=mock_product.title,
            metadata={
                "id": mock_product.id,
                "title": mock_product.title,
                "org_id": mock_product.org_id,
                "channel_id": mock_product.channel_id,
                "catalog_id": mock_product.catalog_id,
                "product_retailer_id": mock_product.product_retailer_id,
            }
        )
        self.mock_storage.save.return_value = mock_document

        result = self.indexer.index(mock_product)

        self.assertEqual(result, mock_document)
        self.mock_storage.save.assert_called_once_with(mock_document)

    def test_index_batch(self):
        mock_products = [
            Product(
                id="1",
                title="Test Product 1",
                org_id="123",
                channel_id="456",
                catalog_id="789",
                product_retailer_id="999"
            ),
            Product(
                id="2",
                title="Test Product 2",
                org_id="123",
                channel_id="456",
                catalog_id="789",
                product_retailer_id="999"
            ),
        ]
        mock_documents = [
            Document(
                page_content=product.title,
                metadata={
                    "id": product.id,
                    "title": product.title,
                    "org_id": product.org_id,
                    "channel_id": product.channel_id,
                    "catalog_id": product.catalog_id,
                    "product_retailer_id": product.product_retailer_id,
                }
            )
            for product in mock_products
        ]
        self.mock_storage.save_batch.return_value = mock_documents

        result = self.indexer.index_batch(mock_products)

        self.assertEqual(result, mock_documents)
        self.mock_storage.save_batch.assert_called_once_with(mock_documents)

    def test_search(self):
        mock_search_query = "Test Query"
        mock_document = Document(
            page_content="Document 1",
            metadata={
                "id": "1",
                "title": "Title 1",
                "org_id": "123",
                "channel_id": "456",
                "catalog_id": "789",
                "product_retailer_id": "999",
            }
        )
        self.mock_storage.search.return_value = [mock_document]

        result = self.indexer.search(mock_search_query)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, mock_document.metadata["title"])
        self.mock_storage.search.assert_called_once_with(mock_search_query, None, 0.1)

if __name__ == "__main__":
    unittest.main()
