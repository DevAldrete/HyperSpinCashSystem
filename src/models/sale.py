from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime
import uuid

class Sale(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    total_amount: float
    tax: float = 0.0
    discount: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "completed"
    
    items: List["SaleItem"] = Relationship(back_populates="sale")
    # We will add the payment relationship after updating the Payment model to avoid circular imports issues if possible, 
    # but SQLModel handles string forward references well.

class SaleItem(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    sale_id: uuid.UUID = Field(foreign_key="sale.id")
    product_id: uuid.UUID = Field(foreign_key="product.id")
    quantity: int
    unit_price: float
    cost_price: float = 0.0
    
    sale: Sale = Relationship(back_populates="items")
