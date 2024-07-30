import os
from celery import Celery

from typing import Dict
from app.indexer.indexer_file_manager import IndexerFileManager
from app.downloaders.s3 import S3FileDownloader

from app.handlers.nexus import NexusRESTClient
from app.text_splitters import TextSplitter, character_text_splitter


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get(
    "CELERY_BROKER_URL", "redis://localhost:6379"
)
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379"
)

@celery.task(name="index_full_file_content")
def index_full_file_content(content_base):
    print("===========================================")
    print(content_base)
    print("===========================================")
    from app.main import main_app
    print("[+ Indexando arquivo inteiro +]")

    file_downloader = S3FileDownloader(
        os.environ.get("AWS_STORAGE_ACCESS_KEY"),
        os.environ.get("AWS_STORAGE_SECRET_KEY")
    )
    content_base_indexer = main_app.content_base_indexer
    text_splitter = TextSplitter(character_text_splitter())
    manager = IndexerFileManager(
        file_downloader,
        content_base_indexer,
        text_splitter,
    )
    index_result: bool = manager.index_full_text(content_base)
    print(f"[+ Resultado da indexação do arquivo inteiro: {index_result} +]")
    # TODO: retry indexing full text or delete embeddings
    NexusRESTClient().index_succedded(
        task_succeded=index_result,
        nexus_task_uuid=content_base.get("task_uuid"),
        file_type=content_base.get("extension_file")
    )



@celery.task(name="index_file")
def index_file_data(content_base: Dict) -> bool:
    from app.main import main_app

    file_downloader = S3FileDownloader(
        os.environ.get("AWS_STORAGE_ACCESS_KEY"),
        os.environ.get("AWS_STORAGE_SECRET_KEY")
    )
    content_base_indexer = main_app.content_base_indexer
    text_splitter = TextSplitter(character_text_splitter())
    manager = IndexerFileManager(
        file_downloader,
        content_base_indexer,
        text_splitter,
    )
    index_result: bool = manager.index_file_url(content_base)

    print("[+ Index File URL result: {index_result} +]")

    if index_result:
        embbed_result: bool = content_base_indexer.check_if_doc_was_embedded_document(
            file_uuid=content_base.get("file_uuid"),
            content_base_uuid=str(content_base.get('content_base')),
        )
        print("[+ Busca dos embeddings: {embbed_result} +]")
        if embbed_result:
            index_full_file_content.delay(content_base)
            return

    NexusRESTClient().index_succedded(
        task_succeded=False,
        nexus_task_uuid=content_base.get("task_uuid"),
        file_type=content_base.get("extension_file")
    )

    return index_result
