"""
Quick database setup script
Run this before testing the pipeline
"""
import os
from pathlib import Path

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_path = Path(".env")
    
    if env_path.exists():
        print("✅ .env file already exists")
        return
    
    print("\n📝 Creating .env file...")
    
    # Get user input
    print("\n" + "="*60)
    print("ENVIRONMENT CONFIGURATION")
    print("="*60)
    
    db_password = input("Enter PostgreSQL password (default: postgres): ").strip() or "postgres"
    groq_api_key = input("Enter Groq API key (get from console.groq.com): ").strip()
    secret_key = input("Enter secret key (press Enter to generate): ").strip()
    
    if not secret_key:
        import secrets
        secret_key = secrets.token_urlsafe(32)
        print(f"Generated secret key: {secret_key}")
    
    env_content = f"""# Database
DATABASE_URL=postgresql://postgres:{db_password}@localhost:5432/ai_analyst_db

# Security
SECRET_KEY={secret_key}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Groq AI
GROQ_API_KEY={groq_api_key}

# Email (Optional - NOT REQUIRED for testing)
# SENDGRID_API_KEY=your-sendgrid-api-key-here
# EMAIL_FROM=noreply@aianalyst.com

# File Upload
MAX_UPLOAD_SIZE=52428800
ALLOWED_EXTENSIONS=pdf,docx

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8000
"""
    
    env_path.write_text(env_content)
    print(f"\n✅ Created .env file at {env_path}")


def check_postgresql():
    """Check if PostgreSQL is installed and running"""
    print("\n" + "="*60)
    print("CHECKING POSTGRESQL")
    print("="*60)
    
    import subprocess
    
    try:
        result = subprocess.run(
            ["psql", "--version"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ PostgreSQL installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ PostgreSQL not found in PATH")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL not installed or not in PATH")
        print("\nPlease install PostgreSQL:")
        print("  Windows: https://www.postgresql.org/download/windows/")
        print("  Mac: brew install postgresql")
        print("  Linux: sudo apt-get install postgresql")
        return False


def create_database():
    """Create the database if it doesn't exist"""
    print("\n" + "="*60)
    print("CREATING DATABASE")
    print("="*60)
    
    import subprocess
    
    db_password = input("Enter PostgreSQL password (default: postgres): ").strip() or "postgres"
    
    # Set password environment variable
    env = os.environ.copy()
    env["PGPASSWORD"] = db_password
    
    # Check if database exists
    try:
        result = subprocess.run(
            ["psql", "-U", "postgres", "-lqt"],
            capture_output=True,
            text=True,
            env=env
        )
        
        if "ai_analyst_db" in result.stdout:
            print("✅ Database 'ai_analyst_db' already exists")
            return True
        
        # Create database
        print("Creating database 'ai_analyst_db'...")
        result = subprocess.run(
            ["psql", "-U", "postgres", "-c", "CREATE DATABASE ai_analyst_db;"],
            capture_output=True,
            text=True,
            env=env
        )
        
        if result.returncode == 0:
            print("✅ Database 'ai_analyst_db' created successfully")
            return True
        else:
            print(f"❌ Failed to create database: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nManual setup:")
        print("  1. Open terminal/command prompt")
        print("  2. Run: psql -U postgres")
        print("  3. Run: CREATE DATABASE ai_analyst_db;")
        print("  4. Run: \\q")
        return False


def setup_alembic():
    """Setup and run Alembic migrations"""
    print("\n" + "="*60)
    print("ALEMBIC MIGRATIONS")
    print("="*60)
    
    os.chdir("backend")
    
    # Check if alembic is initialized
    if not Path("alembic").exists():
        print("Initializing Alembic...")
        os.system("alembic init alembic")
    
    # Update alembic.ini
    print("\n⚠️  IMPORTANT: Update alembic/env.py")
    print("\nAdd these lines after the imports:")
    print("""
from app.config import settings
from app.database import Base
from app.models import user, report, analysis

config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)
target_metadata = Base.metadata
""")
    
    proceed = input("\nHave you updated alembic/env.py? (y/n): ").lower()
    
    if proceed != 'y':
        print("\n⏸️  Please update alembic/env.py and run this script again")
        return False
    
    # Create migration
    print("\nCreating initial migration...")
    os.system('alembic revision --autogenerate -m "Initial migration"')
    
    # Run migration
    print("\nRunning migrations...")
    result = os.system("alembic upgrade head")
    
    if result == 0:
        print("\n✅ Migrations completed successfully")
        return True
    else:
        print("\n❌ Migration failed")
        return False


def main():
    """Main setup function"""
    print("\n" + "🔧"*30)
    print("AI ANALYST AGENT - DATABASE SETUP")
    print("🔧"*30)
    
    # Step 1: Check PostgreSQL
    if not check_postgresql():
        return
    
    # Step 2: Create .env file
    create_env_file()
    
    # Step 3: Create database
    if not create_database():
        return
    
    # Step 4: Setup Alembic
    print("\n" + "="*60)
    print("Next step: Alembic migrations")
    print("="*60)
    
    setup_migrations = input("\nDo you want to setup Alembic migrations? (y/n): ").lower()
    
    if setup_migrations == 'y':
        setup_alembic()
    else:
        print("\n⏭️  Skipping Alembic setup")
        print("\nManual Alembic setup:")
        print("  1. cd backend")
        print("  2. alembic init alembic")
        print("  3. Update alembic/env.py (see TESTING_GUIDE.md)")
        print('  4. alembic revision --autogenerate -m "Initial migration"')
        print("  5. alembic upgrade head")
    
    # Summary
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Start the server: uvicorn app.main:app --reload")
    print("  2. Run tests: python test_pipeline.py")
    print("  3. See TESTING_GUIDE.md for detailed instructions")


if __name__ == "__main__":
    main()
