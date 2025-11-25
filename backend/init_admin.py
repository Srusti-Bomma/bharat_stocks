"""
Initialize admin user
Run this script once to create the admin account
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.database import SessionLocal, init_db
from backend.app.models.user import User, UserRole
from backend.app.auth.utils import get_password_hash
from datetime import datetime

def create_admin():
    # Initialize database tables
    init_db()
    
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == "srushti").first()
        
        if existing_admin:
            # Ensure role and password are correct (re-hash with current scheme)
            existing_admin.role = UserRole.ADMIN
            existing_admin.is_active = True
            existing_admin.hashed_password = get_password_hash("12345")
            db.commit()
            print("✅ Admin user 'srushti' ensured with current hashing scheme.")
            print("   Username: srushti")
            print("   Password: 12345")
            print(f"   Role: {existing_admin.role.value}")
            return
        
        # Create admin user
        admin_user = User(
            username="srushti",
            email="admin@bharatstocks.com",
            hashed_password=get_password_hash("12345"),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin user created successfully!")
        print(f"   Username: srushti")
        print(f"   Password: 12345")
        print(f"   Role: {admin_user.role.value}")
        print(f"\n⚠️  Remember to change the admin password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
