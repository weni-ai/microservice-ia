import unittest
from unittest.mock import Mock
from app.handlers.products import ProductsHandler, Product, ProductSearchRequest, ProductSearchResponse
from app.indexer.interface import IDocumentIndexer
from langchain.docstore.document import Document

class TestProductsHandler(unittest.TestCase):
    def setUp(self):
        self.mock_indexer = Mock(spec=IDocumentIndexer)
        self.handler = ProductsHandler(self.mock_indexer)

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
        self.mock_indexer.index.return_value = mock_document

        result = self.handler.index(mock_product)

        self.assertEqual(result, mock_document)
        self.mock_indexer.index.assert_called_once_with(mock_product)

    def test_batch_index(self):
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
        self.mock_indexer.index_batch.return_value = mock_documents

        result = self.handler.batch_index(mock_products)

        self.assertEqual(result, mock_documents)
        self.mock_indexer.index_batch.assert_called_once_with(mock_products)

    def test_search(self):
        mock_request = ProductSearchRequest(search="Test", filter={"org_id": "123"}, threshold=0.5)
        mock_product = Product(
            id="1",
            title="Test Product",
            org_id="123",
            channel_id="456",
            catalog_id="789",
            product_retailer_id="999"
        )
        self.mock_indexer.search.return_value = [mock_product]

        result = self.handler.search(mock_request)

        self.assertIsInstance(result, ProductSearchResponse)
        self.assertEqual(len(result.products), 1)
        self.assertEqual(result.products[0], mock_product)
        self.mock_indexer.search.assert_called_once_with(mock_request.search, mock_request.filter, mock_request.threshold)

if __name__ == "__main__":
    unittest.main()
