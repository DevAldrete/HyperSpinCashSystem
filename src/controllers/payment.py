from sqlmodel import Session, select
from models.payment import Payment, PaymentProductLink, PaymentStatus, PaymentMethod
from models.item import Product
from db.conn import get_session
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

class PaymentController:
    def __init__(self, session: Optional[Session] = None):
        self.session = session

    def create_payment(self, items: List[Dict[str, Any]], payment_method: PaymentMethod) -> Payment:
        """
        Create a new payment transaction.
        
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
            payment_links = []
            
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
                
                # Prepare link
                link = PaymentProductLink(
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=product.price
                )
                payment_links.append(link)
                
                # Update stock
                product.quantity -= quantity
                if product.quantity == 0:
                    product.in_stock = False
                self.session.add(product)

            # 2. Create Payment record
            payment = Payment(
                amount=total_amount,
                payment_method=payment_method,
                status=PaymentStatus.COMPLETED,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.session.add(payment)
            self.session.flush() # Flush to get the payment ID

            # 3. Associate links with payment
            for link in payment_links:
                link.payment_id = payment.id
                self.session.add(link)

            self.session.commit()
            self.session.refresh(payment)
            return payment
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