from sqlmodel import SQLModel, Field
from typing import Optional
import uuid

class Product(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    description: Optional[str] = None
    price: float
    quantity: int
    in_stock: bool = True

    def __repr__(self):
        return f"Product(id={self.id}, name={self.name}, price={self.price}, quantity={self.quantity}, in_stock={self.in_stock})"
