from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()

# Import models - must import all models so Alembic can detect them
from sqlmodel import SQLModel
from app.models.portfolio import Portfolio
from app.models.user import User
from app.models.chat_message import ChatMessage
from app.models.job import Job

# this is the Alembic Config object
config = context.config

# Override sqlalchemy.url from environment
database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/showcase_db")
# Escape % for ConfigParser (URLs with encoded passwords like %40 for @ need double %%)
escaped_url = database_url.replace("%", "%%") if "%" in database_url else database_url
config.set_main_option("sqlalchemy.url", escaped_url)

# Interpret the config file for Python logging.
# Skip fileConfig if logging is already configured or if config file has issues
try:
    if config.config_file_name is not None:
        fileConfig(config.config_file_name)
except Exception:
    # If logging config fails, use basic logging instead
    import logging
    logging.basicConfig(level=logging.INFO)

# add your model's MetaData object here
# SQLModel uses SQLAlchemy metadata
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

