# from langchain.docstore.document import Document
# from app.handlers.products import Product
# from app.indexer.interface import IDocumentIndexer
# from app.store.interface import IStorage

# class ProductsIndexer(IDocumentIndexer):
#     def __init__(self, storage: IStorage):
#         self.storage = storage

#     def index(self, product: Product) -> Document:
#         doc = Document(
#             page_content=product.title,
#             metadata={
#                 "id": product.id,
#                 "title": product.title,
#                 "org_id": product.org_id,
#                 "channel_id": product.channel_id,
#                 "catalog_id": product.catalog_id,
#                 "product_retailer_id": product.product_retailer_id,
#             }
#         )
#         self.storage.save(doc)
#         return doc

#     def index_batch(self, products: list[Product]) -> list[Document]:
#         docs = []
#         for product in products:
#             doc = Document(
#                 page_content=product.title,
#                 metadata={
#                     "id": product.id,
#                     "title": product.title,
#                     "org_id": product.org_id,
#                     "channel_id": product.channel_id,
#                     "catalog_id": product.catalog_id,
#                     "product_retailer_id": product.product_retailer_id,
#                 }
#             )
#             docs.append(doc)
#         self.storage.save_batch(docs)            
#         return docs

#     def search(self, search, filter=None, threshold=0.1) -> list[Product]:
#         matched_products = self.storage.search(search, filter, threshold)
#         products = []
#         for p in matched_products:
#             products.append(Product(
#                 id=p[0].metadata["id"],
#                 title=p[0].metadata["title"],
#                 org_id=p[0].metadata["org_id"],
#                 channel_id=p[0].metadata["channel_id"],
#                 catalog_id=p[0].metadata["catalog_id"],
#                 product_retailer_id=p[0].metadata["product_retailer_id"],
#             ))
#         return products
from langchain.docstore.document import Document
from app.handlers.products import Product
from app.indexer.interface import IDocumentIndexer
from app.store.interface import IStorage

class ProductsIndexer(IDocumentIndexer):
    def __init__(self, storage: IStorage):
        self.storage = storage

    def _product_to_document(self, product: Product) -> Document:
        metadata = {
            "id": product.id,
            "title": product.title,
            "org_id": product.org_id,
            "channel_id": product.channel_id,
            "catalog_id": product.catalog_id,
            "product_retailer_id": product.product_retailer_id,
        }
        return Document(page_content=product.title, metadata=metadata)

    def index(self, product: Product) -> Document:
        doc = self._product_to_document(product)
        self.storage.save(doc)
        return doc

    def index_batch(self, products: list[Product]) -> list[Document]:
        docs = [self._product_to_document(product) for product in products]
        self.storage.save_batch(docs)
        return docs

    def search(self, search, filter=None, threshold=0.1) -> list[Product]:
        matched_documents = self.storage.search(search, filter, threshold)
        products = [
            Product(
                id=doc.metadata["id"],
                title=doc.metadata["title"],
                org_id=doc.metadata["org_id"],
                channel_id=doc.metadata["channel_id"],
                catalog_id=doc.metadata["catalog_id"],
                product_retailer_id=doc.metadata["product_retailer_id"],
            )
            for doc in matched_documents
        ]
        return products