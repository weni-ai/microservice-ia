from fastapi import APIRouter
from fastapi.logger import logger
from pydantic import BaseModel

from app.handlers import IDocumentHandler
from app.indexer import IDocumentIndexer
from app.downloaders import IFileDownloader

from uuid import UUID
from app.text_splitters.text_splitters import get_split_text
from app.downloaders.s3.file_downloader import download_file, get_s3_bucket_and_file_name


class ContentBaseIndexRequest(BaseModel):
    file_url: str
    document_type: str
    base_uuid: UUID


class ContentBaseIndexResponse(BaseModel):
    file_url: str
    document_type: str
    base_uuid: UUID


def get_raw_data(file_name, file_type):
    from app.loaders.loaders import supported_loaders, DataLoader
    file_path = f'app/files/{file_name}'
    loader = supported_loaders.get(file_type)
    data_loader = DataLoader(loader, file_path)
    return data_loader.raw_text()

def get_loaded_data(file_name, file_type):
    from app.loaders.loaders import supported_loaders, DataLoader
    file_path = f'app/files/{file_name}'
    loader = supported_loaders.get(file_type)
    data_loader = DataLoader(loader, file_path)
    return data_loader.load()


class ContentBaseHandler(IDocumentHandler):
    def __init__(self, content_base_indexer: IDocumentIndexer, file_downloader: IFileDownloader):
        self.content_base_indexer = content_base_indexer
        self.router = APIRouter()
        self.router.add_api_route(
            "/content_base/index", endpoint=self.index, methods=["PUT"]
        )
        self.file_downloader = file_downloader

    def index(self, request: ContentBaseIndexRequest):
        bucket_name, file_name = get_s3_bucket_and_file_name(request.file_url)

        download_file(self.file_downloader, file_name)

        raw_data = get_raw_data(file_name, request.document_type)

        metadatas = {'source': file_name, "content_base_uuid": str(request.base_uuid)}

        texts = get_split_text(raw_data)

        self.content_base_indexer.index(texts, metadatas)

        return ContentBaseIndexResponse(
            file_url=request.file_url,
            document_type=request.document_type,
            base_uuid=request.base_uuid
        )

    def batch_index(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def delete_batch(self):
        raise NotImplementedError

    def search(self):
        raise NotImplementedError
