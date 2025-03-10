# order_service
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Modelo de datos para el pedido
class Order(BaseModel):
    id: str
    user_id: str
    product_id: str
    quantity: int

# Simulación de una base de datos en memoria
database = []

# OrderRepository: Encargado de interactuar con la base de datos
class OrderRepository:
    def save(self, order: dict) -> dict:
        database.append(order)
        print(f"Pedido guardado: {order}")
        return order

    def find_by_user(self, user_id: str) -> List[dict]:
        return [order for order in database if order["user_id"] == user_id]

# OrderService: Contiene la lógica de negocio
class OrderService:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def create_order(self, order_data: dict) -> dict:
        return self.order_repository.save(order_data)

# OrderController: Maneja las solicitudes HTTP
@app.post("/orders")
async def create_order(order: Order):
    order_repository = OrderRepository()
    order_service = OrderService(order_repository)
    return order_service.create_order(order.dict())