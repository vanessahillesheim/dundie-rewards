from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator, condecimal, ConfigDict

from dundie.utils.email import check_valid_email
from dundie.utils.user import generate_simple_password


class InvalidEmailError(Exception):
    ...

class Person(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    email: str = Field(nullable=False, index=True)
    name: str = Field(nullable=False)
    dept: str = Field(nullable=False, index=True)
    role: str = Field(nullable=False)
    currency: str = Field(default="USD")

    balance: "Balance" = Relationship(back_populates="person")
    movement: "Movement" = Relationship(back_populates="person")
    user: "User" = Relationship(back_populates="person")

    model_config = ConfigDict(from_attributes=True)

    @field_validator("email")
    def validate_email(cls, v: str) -> str:
        if not check_valid_email(v):
            raise InvalidEmailError(f"Invalid email for {v!r}")
        return v

    def __str__(self) -> str:
        return f"{self.name} - {self.role}"


class Balance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    person_id: int = Field(foreign_key="person.id")
    value: condecimal(decimal_places=3) = Field(default=0)

    person: Person = Relationship(back_populates="balance")
    
    model_config = ConfigDict(from_attributes=True)


class Movement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    person_id: int = Field(foreign_key="person.id")
    actor: str = Field(nullable=False, index=True)
    value: condecimal(decimal_places=3) = Field(default=0)
    date: datetime = Field(default_factory=lambda: datetime.now())

    person: Person = Relationship(back_populates="movement")
    
    model_config = ConfigDict(from_attributes=True)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    person_id: int = Field(foreign_key="person.id")
    password: str = Field(default_factory=generate_simple_password)

    person: Person = Relationship(back_populates="user")
    
    model_config = ConfigDict(from_attributes=True)