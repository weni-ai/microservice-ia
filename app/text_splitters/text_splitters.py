import os
from abc import ABC, abstractmethod

from typing import Callable, List, Dict
from langchain.schema.document import Document
from langchain.text_splitter import CharacterTextSplitter
from app.util import count_words

DEFAULT_CHUNK_SIZE = os.environ.get("DEFAULT_CHUNK_SIZE", 75)
DEFAULT_CHUNK_OVERLAP = os.environ.get("DEFAULT_CHUNK_OVERLAP", 75)
DEFAULT_SEPARATOR = os.environ.get("DEFAULT_SEPARATOR", "\n")


class ITextSplitter(ABC):  # pragma: no cover

    @abstractmethod
    def split_text(self):
        raise NotImplementedError

    @abstractmethod
    def create_documents(self):
        raise NotImplementedError


class TextSplitter(ITextSplitter):
    def __init__(self, text_splitter: Callable) -> None:
        self.text_splitter = text_splitter

    def split_text(self, content) -> List[str]:
        pages = self.text_splitter.split_text(content)
        return pages

    def create_documents(self, content: List[str], metadatas: List[Dict]) -> List[Document]:
        return self.text_splitter.create_documents(content, metadatas=metadatas)

    def split_documents(self, content: Document):
        return self.text_splitter.split_documents(content)


def character_text_splitter(
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        length_function: Callable = count_words,
        separator: str = DEFAULT_SEPARATOR) -> List:

    text_splitter = CharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=length_function,
        separator=separator,
    )
    return text_splitter


def get_split_text(raw_data: str):
    text_splitter = TextSplitter(character_text_splitter())
    texts = text_splitter.split_text(raw_data)
    return texts
