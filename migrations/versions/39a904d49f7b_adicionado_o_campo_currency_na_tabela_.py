"""Adicionado o campo currency na tabela Person

Revision ID: 39a904d49f7b
Revises: 6279646337bf
Create Date: 2024-01-XX
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

revision = '39a904d49f7b'
down_revision = '6279646337bf'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # SQLite não suporta ALTER COLUMN, então precisamos:
    # 1. Criar uma nova tabela com a estrutura desejada
    # 2. Copiar os dados
    # 3. Renomear as tabelas
    
    # Criar tabela temporária com a coluna currency
    op.execute("""
        CREATE TABLE person_new (
            id INTEGER NOT NULL,
            email VARCHAR NOT NULL,
            name VARCHAR NOT NULL,
            dept VARCHAR NOT NULL,
            role VARCHAR NOT NULL,
            currency VARCHAR NOT NULL DEFAULT 'USD',
            PRIMARY KEY (id)
        )
    """)
    
    # Copiar dados existentes, definindo currency baseado no email
    op.execute("""
        INSERT INTO person_new (id, email, name, dept, role, currency)
        SELECT 
            id, 
            email, 
            name, 
            dept, 
            role,
            CASE email
                WHEN 'schrute@dundermifflin.com' THEN 'EUR'
                WHEN 'glewis@dundermifflin.com' THEN 'BRL'
                WHEN 'pam@dm.com' THEN 'BRL'
                WHEN 'vanessa@dm.com' THEN 'BRL'
                ELSE 'USD'
            END
        FROM person
    """)
    
    # Remover tabela antiga e renomear a nova
    op.execute("DROP TABLE person")
    op.execute("ALTER TABLE person_new RENAME TO person")
    
    # Recriar índices
    op.create_index(op.f('ix_person_id'), 'person', ['id'], unique=False)
    op.create_index(op.f('ix_person_email'), 'person', ['email'], unique=False)
    op.create_index(op.f('ix_person_dept'), 'person', ['dept'], unique=False)

def downgrade() -> None:
    # Para reverter, fazemos o processo inverso
    op.execute("""
        CREATE TABLE person_old (
            id INTEGER NOT NULL,
            email VARCHAR NOT NULL,
            name VARCHAR NOT NULL,
            dept VARCHAR NOT NULL,
            role VARCHAR NOT NULL,
            PRIMARY KEY (id)
        )
    """)
    
    op.execute("""
        INSERT INTO person_old (id, email, name, dept, role)
        SELECT id, email, name, dept, role FROM person
    """)
    
    op.execute("DROP TABLE person")
    op.execute("ALTER TABLE person_old RENAME TO person")
    
    op.create_index(op.f('ix_person_id'), 'person', ['id'], unique=False)
    op.create_index(op.f('ix_person_email'), 'person', ['email'], unique=False)
    op.create_index(op.f('ix_person_dept'), 'person', ['dept'], unique=False)