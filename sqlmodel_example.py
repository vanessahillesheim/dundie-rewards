# para executar este arquivo, ativar o ambiente virtual e no terminal digitar: python sqlmodel_example.py

from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session, select, Relationship

from sqlmodel.sql.expression import Select, SelectOfScalar
SelectOfScalar.inherit_cache = True # type: ignore
Select.inherit_cache = True # type: ignore

class Person(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    balance: "Balance" = Relationship(back_populates="person")

class Balance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    value: int
    person_id: int = Field(foreign_key="person.id")
    person: Person = Relationship(back_populates = "balance")

engine = create_engine("sqlite:///sqlmodel.db", echo=False)
SQLModel.metadata.create_all(bind=engine)

with Session(engine) as session:
    ...
    # person = Person(name="Vanessa")
    # session.add(person)

    # person = Person(name="Albertina")
    # session.add(person)

    # session.commit()

    # SELECT FROM PERSON WHERE person.name == "Albertina"
    # sql = select(Person)
    # results = session.exec(sql)
    # for person in results:
    #     balance = Balance(value=60, person=person)
    #     session.add(balance)
    # session.commit()

# fazer connsulta com informações de person e balance
   # sql = select(Person)
   # results = session.exec(sql)
   # for person in results:
   #     print(person.name, person.balance)

    # sql = select(Balance).where(Balance.value >3)
    # results = session.exec(sql)
    # for balance in results:
    #     print(balance)

# fazer join entre tabelas
    # sql = select(Person, Balance).where(Balance.person_id == Person.id)
    # results = session.exec(sql)
    # for person, balance in results:
    #     print(person.name, balance.value)

    sql = select(Person, Balance).join(Balance, isouter=True)
    results = session.exec(sql)
    for person, balance in results:
        print(person.name, balance.value)