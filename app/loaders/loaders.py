from langchain.document_loaders import TextLoader, PyPDFLoader
from typing import Callable, List
from langchain.schema.document import Document


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


def pdf_loader(file: str) -> Callable:
    loader = PyPDFLoader(file)
    pages = loader.load_and_split()
    return pages


def doc_loader(file: str) -> Callable:
    raise NotImplementedError()


def docx_loader(file: str) -> Callable:
    raise NotImplementedError()


def xlsx_loader(file: str) -> Callable:
    raise NotImplementedError()
