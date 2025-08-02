#!/usr/bin/env python3
"""Script to create an initial admin user for the GUI."""

from core.auth import auth_manager
from storage.database import db_manager

def create_admin_user():
    """Create an admin user for GUI access."""
    # Initialize database
    db_manager.create_tables()
    
    print("Creating admin user for GUI access...")
    
    try:
        session = db_manager.get_session()
        try:
            user = auth_manager.create_user(
                session=session,
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                phone='555-0000',
                address='System Administrator'
            )
        finally:
            session.close()
        print(f"✅ Admin user created successfully!")
        print(f"Email: admin@example.com")
        print(f"Password: admin123")
        print(f"User ID: {user.id}")
        print(f"\nYou can now log in to the GUI at http://localhost:4000")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        print("The user might already exist. Try logging in with:")
        print("Email: admin@example.com")
        print("Password: admin123")

if __name__ == '__main__':
    create_admin_user()