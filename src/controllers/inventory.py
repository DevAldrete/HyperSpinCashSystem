from typing import List, Optional
from models.item import Product
from db.conn import get_session
from sqlmodel import select
import uuid

def add_product(product: Product) -> Product:
    session_gen = get_session()
    session = next(session_gen)
    try:
        session.add(product)
        session.commit()
        session.refresh(product)
        return product
    finally:
        session.close()

def remove_product(product_id: uuid.UUID) -> bool:
    session_gen = get_session()
    session = next(session_gen)
    try:
        product = session.get(Product, product_id)
        if product:
            session.delete(product)
            session.commit()
            return True
        return False
    finally:
        session.close()

def get_product(product_id: uuid.UUID) -> Optional[Product]:
    session_gen = get_session()
    session = next(session_gen)
    try:
        return session.get(Product, product_id)
    finally:
        session.close()

def list_products() -> List[Product]:
    session_gen = get_session()
    session = next(session_gen)
    try:
        statement = select(Product)
        results = session.exec(statement)
        return results.all()
    finally:
        session.close()

def update_product(product_id: uuid.UUID, **kwargs) -> Optional[Product]:
    session_gen = get_session()
    session = next(session_gen)
    try:
        product = session.get(Product, product_id)
        if product:
            for key, value in kwargs.items():
                setattr(product, key, value)
            session.add(product)
            session.commit()
            session.refresh(product)
            return product
        return None
    finally:
        session.close()
