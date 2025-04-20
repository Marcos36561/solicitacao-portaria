"""criar_tabela_condominio

Revision ID: a0b1c2d3f4g5
Revises: 
Create Date: 2025-04-19 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'a0b1c2d3f4g5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1. Criar a tabela de condomínios
    op.create_table(
        'condominio',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('endereco', sa.String(length=200), nullable=True),
        sa.Column('telefone', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('data_criacao', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nome')
    )
    
    # 2. Adicionar a coluna condominio_id na tabela solicitacao
    op.add_column('solicitacao', sa.Column('condominio_id', sa.Integer(), nullable=True))
    
    # 3. Adicionar a restrição de chave estrangeira
    op.create_foreign_key(
        'fk_solicitacao_condominio', 
        'solicitacao', 'condominio', 
        ['condominio_id'], ['id']
    )
    
    # 4. Migrar os dados existentes
    # Criar entradas na tabela de condomínios para cada condomínio único existente
    connection = op.get_bind()
    
    # Obter condomínios únicos da tabela solicitacao
    result = connection.execute("SELECT DISTINCT condominio FROM solicitacao WHERE condominio IS NOT NULL AND condominio != ''")
    condominios_unicos = [row[0] for row in result]
    
    # Inserir cada condomínio único na nova tabela
    for condominio in condominios_unicos:
        connection.execute(
            f"INSERT INTO condominio (nome, is_active, data_criacao) VALUES ('{condominio}', True, '{datetime.now()}')"
        )
        
        # Atualizar o campo condominio_id em todas as solicitações correspondentes
        connection.execute(
            f"""
            UPDATE solicitacao 
            SET condominio_id = (SELECT id FROM condominio WHERE nome = '{condominio}')
            WHERE condominio = '{condominio}'
            """
        )


def downgrade():
    # Remover a chave estrangeira
    op.drop_constraint('fk_solicitacao_condominio', 'solicitacao', type_='foreignkey')
    
    # Remover a coluna condominio_id
    op.drop_column('solicitacao', 'condominio_id')
    
    # Remover a tabela condominio
    op.drop_table('condominio')