from fastapi import APIRouter, HTTPException
from fastapi.logger import logger
from pydantic import BaseModel

from app.handlers import IDocumentHandler
from app.indexer import IDocumentIndexer


class Product(BaseModel):
    facebook_id: str
    title: str
    org_id: str
    channel_id: str
    catalog_id: str
    product_retailer_id: str

    @staticmethod
    def from_metadata(metadata: dict):
        return Product(
            facebook_id=metadata["facebook_id"],
            title=metadata["title"],
            org_id=metadata["org_id"],
            channel_id=metadata["channel_id"],
            catalog_id=metadata["catalog_id"],
            product_retailer_id=metadata["product_retailer_id"],
        )


class ProductIndexRequest(BaseModel):
    catalog_id: str
    product: Product = None


class ProductBatchIndexRequest(BaseModel):
    catalog_id: str
    products: list[Product] = None


class ProductIndexResponse(BaseModel):
    catalog_id: str
    documents: list[str]


class ProductSearchRequest(BaseModel):
    search: str
    filter: dict[str, str] = None
    threshold: float = 1.5


class ProductSearchResponse(BaseModel):
    products: list[Product]


class ProductDeleteRequest(BaseModel):
    catalog_id: str
    product_retailer_ids: list[str]


class ProductsHandler(IDocumentHandler):
    def __init__(self, product_indexer: IDocumentIndexer):
        self.product_indexer = product_indexer
        self.router = APIRouter()
        self.router.add_api_route(
            "/products/index", endpoint=self.index, methods=["PUT"]
        )
        self.router.add_api_route(
            "/products/batch", endpoint=self.batch_index, methods=["PUT"]
        )
        self.router.add_api_route(
            "/products/search", endpoint=self.search, methods=["GET"]
        )
        self.router.add_api_route(
            "/products/index", endpoint=self.delete, methods=["DELETE"]
        )
        self.router.add_api_route(
            "/products/batch", endpoint=self.delete_batch, methods=["DELETE"]
        )

    def index(self, request: ProductIndexRequest):
        try:
            docs = self.product_indexer.index(request.catalog_id, request.product)
            return ProductIndexResponse(catalog_id=request.catalog_id, documents=docs)
        except Exception as e:
            raise HTTPException(status_code=500, detail=[{"msg": str(e)}])

    def batch_index(self, request: ProductBatchIndexRequest):
        try:
            docs = self.product_indexer.index_batch(
                request.catalog_id, request.products
            )
            return ProductIndexResponse(catalog_id=request.catalog_id, documents=docs)
        except Exception as e:
            raise HTTPException(status_code=500, detail=[{"msg": str(e)}])

    def search(self, request: ProductSearchRequest):
        try:
            matched_products = self.product_indexer.search(
                request.search, request.filter, request.threshold
            )
            return ProductSearchResponse(products=matched_products)
        except Exception as e:
            raise HTTPException(status_code=500, detail=[{"msg": str(e)}])

    def delete(
        self,
        catalog_id: str = "",
        product_retailer_id: str = "",
        request: ProductDeleteRequest = None,
    ):
        try:
            if request is not None:
                catalog_id = request.catalog_id
                product_retailer_id = request.product_retailer_ids[0]
            docs = self.product_indexer.delete(catalog_id, product_retailer_id)
            return ProductIndexResponse(catalog_id=catalog_id, documents=docs)
        except Exception as e:
            raise HTTPException(status_code=500, detail=[{"msg": str(e)}])

    def delete_batch(self, request: ProductDeleteRequest):
        try:
            docs = self.product_indexer.delete_batch(
                request.catalog_id, request.product_retailer_ids
            )
            return ProductIndexResponse(catalog_id=request.catalog_id, documents=docs)
        except Exception as e:
            raise HTTPException(status_code=500, detail=[{"msg": str(e)}])
