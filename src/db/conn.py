from sqlmodel import create_engine, Session, SQLModel
import os

# Ensure the storage directory exists
os.makedirs("storage/data", exist_ok=True)

DATABASE_URL = "sqlite:///storage/data/hyperspin.db"

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
