from typing import Callable, List
from langchain.text_splitter import CharacterTextSplitter
from app.util import count_words


class TextSplitter:
    def __init__(self, splitter: Callable, content: str) -> None:
        self.splitter = splitter
        self.content = content

    def split_text(self) -> Callable:
        return self.splitter(self.content)


def character_text_splitter(
        content: str,
        chunk_size: int = 75,
        chunk_overlap: int = 25,
        length_function: Callable = count_words,
        separator: str = "\n",
    ) -> List:
    text_splitter = CharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=length_function,
                separator=separator,
            )
    pages = text_splitter.split_text(content)
    return pages
