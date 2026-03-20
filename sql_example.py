import sqlite3

con = sqlite3.connect("sql_example.db")
con.execute("PRAGMA foreign_keys = ON;")

# criação das tabela do db
# instructions = 
#"""\
"""
CREATE TABLE if not exists person (
    id integer PRIMARY KEY AUTOINCREMENT, 
    name varchar NOT NULL,
    email varchar UNIQUE NOT NULL,
    dept varchar NOT NULL, 
    role varchar NOT NULL
    );
---
CREATE TABLE if not exists balance (
    id integer PRIMARY KEY AUTOINCREMENT, 
    person integer UNIQUE NOT NULL,
    value integer NOT NULL,
    FOREIGN KEY(person) REFERENCES person(id)
    );
---
CREATE TABLE if not exists movement (
    id integer PRIMARY KEY AUTOINCREMENT, 
    person integer NOT NULL,
    value integer NOT NULL,
    date datetime NOT NULL,
    actor varchar NOT NULL,
    FOREIGN KEY(person) REFERENCES person(id)
    );
---
CREATE TABLE if not exists user (
    id integer PRIMARY KEY AUTOINCREMENT, 
    person integer UNIQUE NOT NULL,
    password varchar NOT NULL, 
    FOREIGN KEY(person) REFERENCES person(id)
    );        
"""
#for instruction in instructions.split("---"):
#    con.execute(instruction)


# para adicionar pessoas

# instruction = """\
"""INSERT INTO person (name, email, dept, role)
VALUES ('Albertina', 'betina@gmail.com', 'Sales', 'Manager')

con.execute(instruction)
con.commit()
"""

# para adicionar ponto na tabela balance
# instruction = """\
"""SELECT id, 500
FROM person
WHERE dept = 'Sales';
"""

"""cur = con.cursor()
result = cur.execute(instruction)
for row in result:
    instruction = "INSERT INTO balance (person, value) VALUES (?,?)"
    con.execute(instruction, row)
con.commit()
print(row)"""


# para fazer consulta com informações da tabela person e balance
instruction = """\
SELECT person.name, person.email, balance.value
FROM person
LEFT join balance
WHERE person.id = balance.person
"""

cur = con.cursor()
result = cur.execute(instruction)
for row in result:
    print(row)
    print(row[1])

