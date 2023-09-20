import os
import unittest
from app.config import AppConfig

class TestAppConfig(unittest.TestCase):
    def setUp(self):
        os.environ["INDEX_PRODUCTS_NAME"] = "test_index"
        os.environ["ELASTICSEARCH_URL"] = "http://test.elasticsearch.com"
        os.environ["EMBEDDING_TYPE"] = "test_embedding"
        os.environ["SAGEMAKER_ENDPOINT_NAME"] = "test_endpoint"
        os.environ["SAGEMAKER_REGION_NAME"] = "test_region"
        os.environ["HUGGINGFACE_REPO_ID"] = "test_repo_id"
        os.environ["HUGGINGFACE_TASK"] = "test_task"
        os.environ["HUGGINGFACE_API_TOKEN"] = "test_token"

    def tearDown(self):
        del os.environ["INDEX_PRODUCTS_NAME"]
        del os.environ["ELASTICSEARCH_URL"]
        del os.environ["EMBEDDING_TYPE"]
        del os.environ["SAGEMAKER_ENDPOINT_NAME"]
        del os.environ["SAGEMAKER_REGION_NAME"]
        del os.environ["HUGGINGFACE_REPO_ID"]
        del os.environ["HUGGINGFACE_TASK"]
        del os.environ["HUGGINGFACE_API_TOKEN"]

    def test_config_properties(self):
        config = AppConfig()

        self.assertEqual(config.product_index_name, "test_index")
        self.assertEqual(config.es_url, "http://test.elasticsearch.com")
        self.assertEqual(config.embedding_type, "test_embedding")
        self.assertEqual(config.sagemaker["endpoint_name"], "test_endpoint")
        self.assertEqual(config.sagemaker["region_name"], "test_region")
        self.assertEqual(config.huggingfacehub["repo_id"], "test_repo_id")
        self.assertEqual(config.huggingfacehub["task"], "test_task")
        self.assertEqual(config.huggingfacehub["huggingfacehub_api_token"], "test_token")

if __name__ == "__main__":
    unittest.main()
