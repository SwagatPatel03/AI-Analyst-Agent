"""
Script to check if user exists in database and verify PostgreSQL is running
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
import bcrypt

def check_database_and_user():
    """Check PostgreSQL connection and user existence"""
    
    print("=" * 60)
    print("DATABASE & USER VERIFICATION")
    print("=" * 60)
    
    # Check database URL
    print(f"\n📍 Database URL: {settings.DATABASE_URL}")
    
    try:
        # Try to connect to database
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        print("✅ Successfully connected to PostgreSQL!\n")
        
        # Check if users table exists
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            );
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            print("❌ Users table does not exist!")
            print("   Run: python backend/setup_database.py")
            db.close()
            return
        
        print("✅ Users table exists\n")
        
        # Check for specific user
        email_to_check = "swagatpatel03@gmail.com"
        
        result = db.execute(
            text("SELECT id, email, username, hashed_password FROM users WHERE email = :email"),
            {"email": email_to_check}
        )
        user = result.fetchone()
        
        if user:
            print(f"✅ USER FOUND!")
            print(f"   Email: {user.email}")
            print(f"   Username: {user.username}")
            print(f"   User ID: {user.id}")
            
            # Test password
            test_password = "swagat03"
            password_correct = bcrypt.checkpw(
                test_password.encode('utf-8'),
                user.hashed_password.encode('utf-8') if isinstance(user.hashed_password, str) else user.hashed_password
            )
            
            if password_correct:
                print(f"   ✅ Password 'swagat03' is CORRECT!")
            else:
                print(f"   ❌ Password 'swagat03' is INCORRECT!")
        else:
            print(f"❌ USER NOT FOUND!")
            print(f"   Email '{email_to_check}' does not exist in database")
            print(f"\n   You need to register first:")
            print(f"   1. Go to frontend and click 'Sign Up'")
            print(f"   2. Or use API: POST http://localhost:8000/auth/register")
            print(f"      {{")
            print(f"        \"email\": \"{email_to_check}\",")
            print(f"        \"username\": \"swagatpatel\",")
            print(f"        \"password\": \"swagat03\"")
            print(f"      }}")
        
        # Count total users
        result = db.execute(text("SELECT COUNT(*) FROM users"))
        total_users = result.scalar()
        print(f"\n📊 Total users in database: {total_users}")
        
        if total_users > 0:
            print("\n👥 All users in database:")
            result = db.execute(text("SELECT id, email, username FROM users"))
            for user in result.fetchall():
                print(f"   - {user.email} (username: {user.username}, id: {user.id})")
        
        db.close()
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: Could not connect to PostgreSQL!")
        print(f"   Error: {str(e)}")
        print(f"\n   Possible issues:")
        print(f"   1. PostgreSQL is not running")
        print(f"   2. Wrong database credentials")
        print(f"   3. Database 'ai_analyst_db' doesn't exist")
        print(f"\n   To fix:")
        print(f"   1. Start PostgreSQL service")
        print(f"   2. Run: python backend/setup_database.py")
        print("\n" + "=" * 60)

if __name__ == "__main__":
    check_database_and_user()
