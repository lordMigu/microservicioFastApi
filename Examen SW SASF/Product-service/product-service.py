# product_service
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Modelo de datos para el producto
class Product(BaseModel):
    id: str
    name: str
    category: str
    price: float

# Simulación de una base de datos en memoria
database = []

# ProductRepository: Encargado de interactuar con la base de datos
class ProductRepository:
    def save(self, product: dict) -> dict:
        database.append(product)
        print(f"Producto guardado: {product}")
        return product

    def find_by_category(self, category: str) -> List[dict]:
        return [product for product in database if product["category"] == category]

# ProductService: Contiene la lógica de negocio
class ProductService:
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository

    def create_product(self, product_data: dict) -> dict:
        return self.product_repository.save(product_data)

# ProductController: Maneja las solicitudes HTTP
@app.post("/products")
async def create_product(product: Product):
    product_repository = ProductRepository()
    product_service = ProductService(product_repository)
    return product_service.create_product(product.dict())