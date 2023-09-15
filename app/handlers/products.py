from fastapi import APIRouter, HTTPException
from fastapi.logger import logger
from app.handlers.interface import IDocumentHandler
from app.indexer.interface import IDocumentIndexer
from pydantic import BaseModel
from langchain.docstore.document import Document

class Product(BaseModel):
    id: str
    title: str
    org_id: str
    channel_id: str
    catalog_id: str
    product_retailer_id: str
    shop: str | None = None

class ProductSearchRequest(BaseModel):
    search: str
    filter: dict[str, str] = None
    threshold: float

class ProductSearchResponse(BaseModel):
    products: list[Product]

class ProductsHandler(IDocumentHandler):
    def __init__(self, product_indexer: IDocumentIndexer):
        self.product_indexer = product_indexer
        self.router = APIRouter()
        self.router.add_api_route("/products/index", endpoint=self.index, methods=["POST"])
        self.router.add_api_route("/products/batch", endpoint=self.batch_index, methods=["POST"])
        self.router.add_api_route("/products/search", endpoint=self.search, methods=["GET"])
        
    def index(self, product: Product):
        try:
            return self.product_indexer.index(product)
        except Exception as e:
            logger.error(msg=str(e))
            raise HTTPException(status_code=500, detail=[{"msg": str(e)}])
    
    def batch_index(self, products: list[Product]):
        try:
            return self.product_indexer.index_batch(products)
        except Exception as e:
            logger.error(msg=str(e))
            raise HTTPException(status_code=500, detail=[{"msg": str(e)}])

    def search(self, request: ProductSearchRequest):
        try:
            matched_products = self.product_indexer.search(request.search, request.filter, request.threshold)
            return ProductSearchResponse(
                products=matched_products
            )
        except Exception as e:
            logger.error(msg=str(e))
            raise HTTPException(status_code=500, detail=[{"msg": str(e)}])
