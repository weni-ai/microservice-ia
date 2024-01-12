from langchain.document_loaders import (
    TextLoader, PyPDFLoader, UnstructuredExcelLoader,
    UnstructuredWordDocumentLoader, Docx2txtLoader
)
from typing import Callable, List
from langchain.schema.document import Document
from abc import ABC, abstractmethod
from app.text_splitters import ITextSplitter


class DocumentLoader(ABC):

    @abstractmethod
    def load(self):
        pass


class DataLoaderCls:
    def __init__(self, loader: DocumentLoader, file: str) -> None:
        self.loader = loader(file)
        self.file = file

    def load(self) -> List[Document]:
        return self.loader.load()
    
    def load_and_split_text(self, text_splitter: ITextSplitter) -> List[Document]:
        return self.loader.load_and_split_text(text_splitter)

    def raw_text(self) -> str:
        return self.loader.raw_text()


class DataLoader:
    def __init__(self, loader: Callable, file: str) -> None:
        self.loader = loader
        self.file = file

    def load(self) -> List[Document]:
        return self.loader(self.file)

    def raw_text(self) -> str:
        pages = self.load()
        raw_text = ""
        for i, page in enumerate(pages):
            text = page.page_content
            if text:
                raw_text += text.lower()
        return raw_text


def txt_loader(file: str) -> Callable:
    loader = TextLoader(file)
    return loader.load()


class PDFLoader(DocumentLoader):
    def __init__(self, file: str) -> None:
        self.loader = PyPDFLoader(file)

    def load(self) -> List[Document]:
        pages = self.loader.load_and_split()
        return pages

    def load_and_split_text(self, text_splitter: ITextSplitter) -> List[Document]:
        pages = self.load()
        split_pages = []

        for page in pages:
            page_content = page.page_content.lower()
            metadatas = page.metadata
            metadatas.update({"full_page": page_content})

            text_chunks = text_splitter.split_text(page_content)
            for chunk in text_chunks:
                split_pages.append(Document(page_content=chunk, metadata=metadatas))

        return split_pages

    def raw_text(self) -> str:
        pages = self.load()
        raw_text = ""
        for i, page in enumerate(pages):
            text = page.page_content
            if text:
                raw_text += text.lower()
        return raw_text


def pdf_loader(file: str) -> Callable:
    loader = PyPDFLoader(file)
    pages = loader.load_and_split()
    return pages


def docx_loader(file: str) -> Callable:
    loader = Docx2txtLoader(file)
    return loader.load()


def u_docx_loader(file: str) -> Callable:
    """Same as docx_loader but using Unstructured"""
    loader = UnstructuredWordDocumentLoader(file)
    return loader.load()


def xlsx_loader(file: str) -> Callable:
    """Loads .xlsx and .xls files"""
    loader = UnstructuredExcelLoader(file, mode="elements")
    return loader.load()
