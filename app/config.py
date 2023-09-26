import os


class AppConfig:
    def __init__(self):
        self.product_index_name = os.environ.get(
            "INDEX_PRODUCTS_NAME", "catalog_products"
        )
        self.es_url = os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")
        self.embedding_type = os.environ.get("EMBEDDING_TYPE", "sagemaker")
        self.sagemaker = {
            "endpoint_name": os.environ.get(
                "SAGEMAKER_ENDPOINT_NAME",
                "huggingface-pytorch-inference-2023-07-28-21-01-20-147",
            ),
            "region_name": os.environ.get("SAGEMAKER_REGION_NAME", "us-east-1"),
        }
        self.huggingfacehub = {
            "repo_id": os.environ.get(
                "HUGGINGFACE_REPO_ID", "sentence-transformers/all-MiniLM-L6-v2"
            ),
            "task": os.environ.get("HUGGINGFACE_TASK", "feature-extraction"),
            "huggingfacehub_api_token": os.environ.get(
                "HUGGINGFACE_API_TOKEN", "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"
            ),
        }
