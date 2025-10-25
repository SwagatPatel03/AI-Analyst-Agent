"""
Quick database setup - Creates database and tables
Run this after PostgreSQL is running and .env is configured
"""
import os
import sys

print("\n" + "="*60)
print("QUICK DATABASE SETUP")
print("="*60)

# Step 1: Create database
print("\n📦 Step 1: Creating database...")
print("Please run this command and enter your password:")
print('psql -U postgres -c "CREATE DATABASE ai_analyst_db;"')
print("\nIf it says 'database already exists', that's OK!")

input("\nPress Enter after you've run the command above...")

# Step 2: Initialize Alembic (if not done)
print("\n📦 Step 2: Initializing Alembic...")
if not os.path.exists("alembic"):
    print("Running: alembic init alembic")
    os.system("alembic init alembic")
else:
    print("✅ Alembic already initialized")

# Step 3: Update alembic.ini
print("\n📦 Step 3: Updating alembic.ini...")
try:
    with open("alembic.ini", "r") as f:
        content = f.read()
    
    # Comment out the default sqlalchemy.url
    if "sqlalchemy.url = driver://user:pass@localhost/dbname" in content:
        content = content.replace(
            "sqlalchemy.url = driver://user:pass@localhost/dbname",
            "# sqlalchemy.url = driver://user:pass@localhost/dbname"
        )
    
    with open("alembic.ini", "w") as f:
        f.write(content)
    
    print("✅ alembic.ini updated")
except Exception as e:
    print(f"⚠️  Could not update alembic.ini: {e}")

# Step 4: Update alembic/env.py
print("\n📦 Step 4: Updating alembic/env.py...")
env_py_content = '''from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import your models and config
from app.config import settings
from app.database import Base
from app.models import user, report, analysis

# this is the Alembic Config object
config = context.config

# Set the database URL from settings
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

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
'''

try:
    with open("alembic/env.py", "w") as f:
        f.write(env_py_content)
    print("✅ alembic/env.py updated")
except Exception as e:
    print(f"❌ Could not update alembic/env.py: {e}")
    print("\nPlease manually update alembic/env.py with the content from the guide.")

# Step 5: Create initial migration
print("\n📦 Step 5: Creating initial migration...")
print("Running: alembic revision --autogenerate -m 'Initial migration'")
os.system('alembic revision --autogenerate -m "Initial migration"')

# Step 6: Run migrations
print("\n📦 Step 6: Running migrations...")
print("Running: alembic upgrade head")
result = os.system("alembic upgrade head")

if result == 0:
    print("\n" + "="*60)
    print("✅ DATABASE SETUP COMPLETE!")
    print("="*60)
    print("\nYour database is ready!")
    print("\nNext steps:")
    print("1. Start the server: uvicorn app.main:app --reload")
    print("2. Run tests: python test_pipeline.py")
else:
    print("\n" + "="*60)
    print("❌ MIGRATION FAILED")
    print("="*60)
    print("\nPlease check the error messages above.")
    print("Common issues:")
    print("- PostgreSQL not running")
    print("- Wrong password in .env file")
    print("- Database doesn't exist")
