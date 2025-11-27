from sqlmodel import SQLModel, Field
import uuid
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str
    role: Role = Field(default=Role.USER)
    email: str
    password_hash: str = Field(repr=False)
    is_active: bool = True

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email}, is_active={self.is_active})"
