from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from enum import Enum
from datetime import datetime
import uuid

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"

class PaymentProductLink(SQLModel, table=True):
    payment_id: uuid.UUID = Field(foreign_key="payment.id", primary_key=True)
    product_id: uuid.UUID = Field(foreign_key="product.id", primary_key=True)
    quantity: int = Field(default=1)
    unit_price: float = Field(description="Price of the product at the time of purchase")

class Payment(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    amount: float
    currency: str = Field(default="USD")
    payment_method: PaymentMethod
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    transaction_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to items (products)
    # Note: We can't easily access the 'quantity' in the link table via a direct list of Products 
    # if we use a simple many-to-many relationship. 
    # Usually, it's better to access the link table directly if we need the quantities.
    items: List["PaymentProductLink"] = Relationship(back_populates=None)

    def __repr__(self):
        return f"Payment(id={self.id}, amount={self.amount}, status={self.status}, created_at={self.created_at})"
