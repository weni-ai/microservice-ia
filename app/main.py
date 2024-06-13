import sentry_sdk
import os
from elasticsearch import Elasticsearch
from elasticapm.contrib.starlette import ElasticAPM, make_apm_client
from fastapi import FastAPI
from langchain.embeddings import HuggingFaceHubEmbeddings, CohereEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.vectorstores import ElasticVectorSearch, VectorStore, ElasticsearchStore

from app.handlers import IDocumentHandler
from app.handlers.products import ProductsHandler
from app.indexer import IDocumentIndexer
from app.indexer.products import ProductsIndexer
from app.store.elasticsearch_vector_store import (
    ElasticsearchVectorStoreIndex,
    ContentBaseElasticsearchVectorStoreIndex
)
from app.config import AppConfig
from app.util import ContentHandler


from app.handlers.content_bases import ContentBaseHandler
from app.indexer.content_bases import ContentBaseIndexer
from app.embedders.embedders import SagemakerEndpointEmbeddingsKeys


class App:
    api: FastAPI
    config: AppConfig
    embeddings: Embeddings
    vectorstore: VectorStore
    products_handler: IDocumentHandler
    products_indexer: IDocumentIndexer

    def __init__(self, config: AppConfig):
        self.config = config
        if config.embedding_type == "huggingface":
            self.embeddings = HuggingFaceHubEmbeddings(
                repo_id=config.huggingfacehub["repo_id"],
                task=config.huggingfacehub["task"],
                huggingfacehub_api_token=config.huggingfacehub[
                    "huggingfacehub_api_token"
                ],
            )
        elif config.embedding_type == "cohere":
            self.embeddings = CohereEmbeddings(
                model=config.cohere["model"],
                cohere_api_key=config.cohere["cohere_api_key"]
            )
        else:  # sagemaker by default
            content_handler = ContentHandler()
            self.embeddings = SagemakerEndpointEmbeddingsKeys(
                aws_key=config.sagemaker_aws["aws_key"],
                aws_secret=config.sagemaker_aws["aws_secret"],
                endpoint_name=config.sagemaker_aws["endpoint_name"],
                region_name=config.sagemaker_aws["region_name"],
                content_handler=content_handler,
            )

        if config.sentry_dsn != "":
            sentry_sdk.init(
                dsn=config.sentry_dsn,
            )

        self.api = FastAPI()
        self.vectorstore = ElasticVectorSearch(
            elasticsearch_url=config.es_url,
            index_name=config.product_index_name,
            embedding=self.embeddings,
        )
        self.vectorstore.client = Elasticsearch(
            hosts=config.es_url, timeout=int(config.es_timeout)
        )
        self.elasticStore = ElasticsearchVectorStoreIndex(self.vectorstore)
        self.products_indexer = ProductsIndexer(self.elasticStore)
        self.products_handler = ProductsHandler(self.products_indexer)
        self.api.include_router(self.products_handler.router)

        self.content_base_vectorstore = ElasticsearchStore(
            es_url=config.es_url,
            index_name=config.content_base_index_name,
            embedding=self.embeddings,
            strategy=ElasticsearchStore.ExactRetrievalStrategy()
        )
        self.content_base_vectorstore.client = Elasticsearch(
            hosts=config.es_url, timeout=int(config.es_timeout)
        )
        self.custom_elasticStore = ContentBaseElasticsearchVectorStoreIndex(self.content_base_vectorstore)
        self.content_base_indexer = ContentBaseIndexer(self.custom_elasticStore)
        self.content_base_handler = ContentBaseHandler(self.content_base_indexer)
        self.api.include_router(self.content_base_handler.router)

        # APM Configuration

        apm_config = {
            'SERVICE_NAME': os.environ.get('APM_SERVICE_NAME'),
            'SECRET_TOKEN': os.environ.get('APM_SECRET_TOKEN'),
            'SERVER_URL': os.environ.get('APM_SERVER_URL'),
            'ENVIRONMENT': os.environ.get('APM_ENVIRONMENT'),
        }

        apm_CLIENT = make_apm_client(apm_config)
        self.api.add_middleware(ElasticAPM, client=apm_CLIENT)


config = AppConfig()
main_app = App(config)


@main_app.api.get('/', status_code=200)
def home():
    return {}
