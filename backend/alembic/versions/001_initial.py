# backend/alembic/versions/001_initial.py
# 创建数据库迁移文件
from alembic import op
import sqlalchemy as sa

def upgrade():
    # 用户表
    op.create_table('users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(10), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )