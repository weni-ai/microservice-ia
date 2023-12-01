import os
from celery import Celery

from app.text_splitters.text_splitters import get_split_text
from app.loaders import load_file_and_get_raw_text
from typing import List, Dict
from fastapi.logger import logger
from app.downloaders.exceptions import FileDownloaderException
from app.downloaders import download_file


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get(
        "CELERY_BROKER_URL", "redis://localhost:6379"
    )
celery.conf.result_backend = os.environ.get(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379"
    )


def get_file_metadata(content_base: Dict) -> Dict[str, str]:
    return {
            'source': content_base.get("filename"),
            "content_base_uuid": str(content_base.get('content_base'))
        }


@celery.task(name="index_file")
def index_file_data(content_base: Dict) -> bool:
    from app.main import main_app

    filename: str = content_base.get("filename")

    try:
        download_file(main_app.file_downloader, filename)
    except FileDownloaderException as err:
        logger.exception(err)
        return False

    file_raw_text: str = load_file_and_get_raw_text(
            filename, content_base.get('extension_file')
        )
    metadatas: Dict[str, str] = get_file_metadata(content_base)
    texts: List[str] = get_split_text(file_raw_text)

    try:
        main_app.content_ai_indexer.index(texts, metadatas)
        return True
    except Exception as e:  # TODO: handle exceptions
        logger.exception(e)
        return False
