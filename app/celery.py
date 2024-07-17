import os
from celery import Celery

from typing import Dict, List

from langchain.docstore.document import Document

from app.store import IStorage
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


@celery.task(name="index_file")
def index_file_data(content_base: Dict) -> bool:
    from app.main import main_app
    print("Start task")

    file_downloader = S3FileDownloader(
        os.environ.get("AWS_STORAGE_ACCESS_KEY"),
        os.environ.get("AWS_STORAGE_SECRET_KEY")
    )
    print("File downloader created")
    content_base_indexer = main_app.content_base_indexer
    text_splitter = TextSplitter(character_text_splitter())
    print("Text splitter created")

    manager = IndexerFileManager(
        file_downloader,
        content_base_indexer,
        text_splitter,
    )
    print("Start indexing")
    index_result: bool = manager.index_file_url(content_base)
    print("End indexing")
    embbed_result: bool = content_base_indexer.check_if_doc_was_embedded_document(
        file_uuid=content_base.get("file_uuid"),
        content_base_uuid=str(content_base.get('content_base')),
    )
    print("Embedding result")

    index_result = index_result and embbed_result

    NexusRESTClient().index_succedded(
        task_succeded=index_result,
        nexus_task_uuid=content_base.get("task_uuid"),
        file_type=content_base.get("extension_file")
    )

    return index_result


@celery.task(name="save_file")
def start_save(
    docs: List[Document],
    search_results: List[Dict]
) -> bool:
    from app.main import main_app

    ids = []
    if len(search_results) > 0:
        ids = [item["_id"] for item in search_results]
        main_app.content_base_vectorstore.delete(ids=ids)

    storage = main_app.content_base_vectorstore
    return storage.save(docs)
