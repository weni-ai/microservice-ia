import unittest
from app.text_splitters.text_splitters import (
    TextSplitter, character_text_splitter, get_split_text
)
from lorem_text import lorem

from typing import List
from langchain.schema.document import Document


class TestProductsHandler(unittest.TestCase):
    def setUp(self):
        self.text = lorem.paragraphs(5)

    def test_character_text_splitter_split_text(self):
        chunk_size = 75
        splitter = TextSplitter(character_text_splitter(chunk_size=chunk_size))
        chunks = splitter.split_text(self.text)
        self.assertEqual(type(chunks), list)
        [self.assertGreaterEqual(len(chunk), chunk_size) for chunk in chunks]

    def test_character_text_splitter_create_documents(self):
        chunk_size = 75
        metadatas = [{"text_size": len(self.text)}]
        text_list = [self.text]
        splitter = TextSplitter(character_text_splitter(chunk_size=chunk_size))
        docs = splitter.create_documents(text_list, metadatas)
        self.assertIs(list, type(docs))
        self.assertIs(Document, type(docs[0]))

    def test_character_text_splitter_split_documents(self):
        chunk_size = 75
        splitter = TextSplitter(character_text_splitter(chunk_size=chunk_size))
        doc = Document(page_content=self.text, metadata={"text_size": len(self.text)})
        docs = splitter.split_documents([doc])
        self.assertIs(list, type(docs))

    def test_get_split_text(self):
        texts: List[str] = get_split_text(self.text)
        self.assertIs(list, type(texts))
