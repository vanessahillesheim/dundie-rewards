from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base() # factory

class Person (Base):
    __tablename__ ="person"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255))

engine = create_engine("sqlite:///tmp/database.db")

Base.metadata.create_all(bind=engine)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

session = SessionLocal()

'''
# Para inserir pessoas na tabela Personson = Person(name="Ana Julia")
session.add(person)

person = Person(name="Pedro")
session.add(person)

session.commit()

'''
# Para fazer query=consulta 
results = session.query(Person).filter(Person.name == "Pedro")
for result in results:
    print(result.name)