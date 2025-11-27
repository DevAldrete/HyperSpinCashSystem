from sqlmodel import Session, select
from models.payment import Payment, PaymentStatus, PaymentMethod
from models.sale import Sale, SaleItem
from models.item import Product
from db.conn import get_session
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

class PaymentController:
    def __init__(self, session: Optional[Session] = None):
        self.session = session

    def create_sale(self, items: List[Dict[str, Any]], payment_method: PaymentMethod) -> Sale:
        """
        Create a new sale transaction.
        
        items: List of dicts with 'product_id' and 'quantity'
        payment_method: Method of payment
        """
        # If session was not provided, create a new one for this transaction
        local_session = False
        if not self.session:
            session_gen = get_session()
            self.session = next(session_gen)
            local_session = True

        try:
            total_amount = 0.0
            sale_items = []
            
            # 1. Validate items and calculate total
            for item in items:
                product_id = item['product_id']
                quantity = item['quantity']
                
                product = self.session.get(Product, product_id)
                if not product:
                    raise ValueError(f"Product with ID {product_id} not found")
                
                if not product.in_stock or product.quantity < quantity:
                    raise ValueError(f"Not enough stock for product: {product.name}")
                
                # Calculate line total
                line_total = product.price * quantity
                total_amount += line_total
                
                # Prepare SaleItem
                sale_item = SaleItem(
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=product.price,
                    cost_price=product.cost_price
                )
                sale_items.append(sale_item)
                
                # Update stock
                product.quantity -= quantity
                if product.quantity == 0:
                    product.in_stock = False
                self.session.add(product)

            # 2. Create Sale record
            sale = Sale(
                total_amount=total_amount,
                status="completed",
                created_at=datetime.now()
            )
            self.session.add(sale)
            self.session.flush() # Flush to get the sale ID

            # 3. Associate items with sale
            for sale_item in sale_items:
                sale_item.sale_id = sale.id
                self.session.add(sale_item)
            
            # 4. Create Payment record
            payment = Payment(
                sale_id=sale.id,
                amount=total_amount,
                payment_method=payment_method,
                status=PaymentStatus.COMPLETED,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.session.add(payment)

            self.session.commit()
            self.session.refresh(sale)
            return sale
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            if local_session:
                self.session.close()
                self.session = None

    def get_payment(self, payment_id: uuid.UUID) -> Optional[Payment]:
        local_session = False
        if not self.session:
            session_gen = get_session()
            self.session = next(session_gen)
            local_session = True
            
        try:
            return self.session.get(Payment, payment_id)
        finally:
            if local_session:
                self.session.close()
                self.session = None

    def get_all_payments(self) -> List[Payment]:
        local_session = False
        if not self.session:
            session_gen = get_session()
            self.session = next(session_gen)
            local_session = True
            
        try:
            statement = select(Payment).order_by(Payment.created_at.desc())
            return self.session.exec(statement).all()
        finally:
            if local_session:
                self.session.close()
                self.session = None