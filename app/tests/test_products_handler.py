import unittest
from unittest.mock import Mock
from app.handlers.products import ProductsHandler, Product, ProductSearchRequest, ProductSearchResponse, ProductIndexRequest, ProductBatchIndexRequest, ProductIndexResponse, ProductDeleteRequest
from app.indexer import IDocumentIndexer
from fastapi import HTTPException

class TestProductsHandler(unittest.TestCase):
    def setUp(self):
        self.mock_indexer = Mock(spec=IDocumentIndexer)
        self.handler = ProductsHandler(self.mock_indexer)

    def test_index(self):
        catalog_id = "789"
        mock_product = Product(
            title="Test Product",
            org_id="123",
            channel_id="456",
            catalog_id=catalog_id,
            product_retailer_id="999"
        )
        mock_doc_id = "28ca2dcd-3497-49d5-a1cc-1c3e652fc49c"
        self.mock_indexer.index.return_value = [mock_doc_id]
        

        mock_product_index_request = ProductIndexRequest(catalog_id=catalog_id, product=mock_product)
        result = self.handler.index(mock_product_index_request)

        expected_product_index_response = ProductIndexResponse(catalog_id=catalog_id, documents=[mock_doc_id])
        self.assertEqual(result, expected_product_index_response)
        self.mock_indexer.index.assert_called_once_with(catalog_id, mock_product)

    def test_index_with_exception(self):
        catalog_id = "789"
        mock_product = Product(
            title="Test Product",
            org_id="123",
            channel_id="456",
            catalog_id=catalog_id,
            product_retailer_id="999"
        )
        self.mock_indexer.index.side_effect = RuntimeError("some error")
    
        mock_product_index_request = ProductIndexRequest(catalog_id=catalog_id, product=mock_product)
        
        with self.assertRaises(HTTPException) as context:
            self.handler.index(mock_product_index_request)

        self.assertEqual(context.exception.detail[0]["msg"], "some error")

    def test_batch_index(self):
        catalog_id = "789"
        mock_products = [
            Product(
                title="Test Product 1",
                org_id="123",
                channel_id="456",
                catalog_id=catalog_id,
                product_retailer_id="998"
            ),
            Product(
                title="Test Product 2",
                org_id="123",
                channel_id="456",
                catalog_id=catalog_id,
                product_retailer_id="999"
            ),
        ]

        mock_ids = ["518c3834-e715-4f4d-9976-b4b318698e74", "4b4b9f6f-e177-4709-bd00-429f0675a0c4"]
        
        self.mock_indexer.index_batch.return_value = mock_ids

        mock_batch_index_request = ProductBatchIndexRequest(catalog_id=catalog_id, products=mock_products)
        result = self.handler.batch_index(mock_batch_index_request)

        expected_batch_index_response = ProductIndexResponse(catalog_id=catalog_id, documents=mock_ids)
        self.assertEqual(result, expected_batch_index_response)
        self.mock_indexer.index_batch.assert_called_once_with(catalog_id, mock_products)
    
    def test_batch_index_with_exception(self):
        catalog_id = "789"
        mock_products = [
            Product(
                title="Test Product 1",
                org_id="123",
                channel_id="456",
                catalog_id=catalog_id,
                product_retailer_id="998"
            ),
            Product(
                title="Test Product 2",
                org_id="123",
                channel_id="456",
                catalog_id=catalog_id,
                product_retailer_id="999"
            ),
        ]

        self.mock_indexer.index_batch.side_effect = RuntimeError("some error")

        with self.assertRaises(HTTPException) as context:
            mock_batch_index_request = ProductBatchIndexRequest(catalog_id=catalog_id, products=mock_products)
            self.handler.batch_index(mock_batch_index_request)
        self.assertEqual(context.exception.detail[0]["msg"], "some error")

    def test_search(self):
        mock_request = ProductSearchRequest(search="Test", filter={"catalog_id": "789"}, threshold=0.5)
        mock_product = Product(
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

    def test_search_with_exception(self):
        mock_request = ProductSearchRequest(search="Test", filter={"catalog_id": "789"}, threshold=0.5)
        mock_product = Product(
            title="Test Product",
            org_id="123",
            channel_id="456",
            catalog_id="789",
            product_retailer_id="999"
        )
        self.mock_indexer.search.side_effect = RuntimeError("some error")

        with self.assertRaises(HTTPException) as context:
            self.handler.search(mock_request)
        self.assertEqual(context.exception.detail[0]["msg"], "some error")

    def test_delete(self):
        catalog_id = "789"
        product_retailer_ids = ["p123"]
        mock_id = "4d0c1730-133d-4b49-b407-5141bd571cca"
        mock_request = ProductDeleteRequest(catalog_id=catalog_id, product_retailer_ids=product_retailer_ids)
        self.mock_indexer.delete.return_value = [mock_id]
        result = self.handler.delete(request=mock_request)
        self.assertEqual(result, ProductIndexResponse(catalog_id=catalog_id, documents=[mock_id]))

    def test_delete_with_exception(self):
        catalog_id = "789"
        product_retailer_ids = ["p123"]
        mock_request = ProductDeleteRequest(catalog_id=catalog_id, product_retailer_ids=product_retailer_ids)
        self.mock_indexer.delete.side_effect = RuntimeError("some error")
        with self.assertRaises(HTTPException) as context:
            self.handler.delete(request=mock_request)
        self.assertEqual(context.exception.detail[0]["msg"], "some error")

    def test_delete_batch(self):
        catalog_id = "789"
        product_retailer_ids = ["p123", "p124"]
        mock_ids = ["4d0c1730-133d-4b49-b407-5141bd571cca", "9d063d4b-20f7-4fcd-9751-247c97357efb"]
        mock_request = ProductDeleteRequest(catalog_id=catalog_id, product_retailer_ids=product_retailer_ids)
        self.mock_indexer.delete_batch.return_value = mock_ids
        result = self.handler.delete_batch(request=mock_request)
        self.assertEqual(result, ProductIndexResponse(catalog_id=catalog_id, documents=mock_ids))
        
    def test_delete_batch_with_exception(self):
        catalog_id = "789"
        product_retailer_ids = ["p123", "p124"]
        mock_request = ProductDeleteRequest(catalog_id=catalog_id, product_retailer_ids=product_retailer_ids)
        self.mock_indexer.delete_batch.side_effect = RuntimeError("some error")
        with self.assertRaises(HTTPException) as context:
            self.handler.delete_batch(request=mock_request)
        self.assertEqual(context.exception.detail[0]["msg"], "some error")