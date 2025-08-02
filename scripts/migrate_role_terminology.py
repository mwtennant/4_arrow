#!/usr/bin/env python3
"""Migration script for role terminology refactor.

This script migrates the database from legacy is_member column (if it exists)
to the new role-based system using ProfileRole enum values.

Usage:
    python scripts/migrate_role_terminology.py [--dry-run] [--reverse]
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import User, ProfileRole
from storage.database import db_manager
from sqlalchemy import text, Column, String, inspect
from sqlalchemy.exc import SQLAlchemyError


class RoleTerminologyMigration:
    """Handles migration between legacy member terminology and new role system."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.session = None
        
    def __enter__(self):
        """Context manager entry."""
        self.session = db_manager.get_session()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.session:
            if exc_type is not None:
                self.session.rollback()
            self.session.close()
    
    def check_migration_status(self) -> dict:
        """Check current migration status.
        
        Returns:
            dict: Status information about migration state
        """
        inspector = inspect(self.session.bind)
        table_columns = inspector.get_columns('users')
        column_names = [col['name'] for col in table_columns]
        
        has_role_column = 'role' in column_names
        has_is_member_column = 'is_member' in column_names
        
        # Count users and their current roles
        total_users = self.session.query(User).count()
        
        role_counts = {}
        if total_users > 0:
            # Count by computed role since role column may not exist yet
            for user in self.session.query(User).all():
                role = user.get_role()
                role_counts[role.value] = role_counts.get(role.value, 0) + 1
        
        return {
            'has_role_column': has_role_column,
            'has_is_member_column': has_is_member_column,
            'total_users': total_users,
            'role_distribution': role_counts,
            'migration_needed': not has_role_column or has_is_member_column
        }
    
    def add_role_column(self) -> None:
        """Add role column to users table if it doesn't exist."""
        print("📋 Adding role column to users table...")
        
        if self.dry_run:
            print("   [DRY RUN] Would execute: ALTER TABLE users ADD COLUMN role VARCHAR(32)")
            return
            
        try:
            # Add role column with default value
            self.session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN role VARCHAR(32) DEFAULT 'registered_user'
            """))
            
            # Add check constraint for valid role values
            self.session.execute(text("""
                ALTER TABLE users 
                ADD CONSTRAINT check_role_valid 
                CHECK (role IN ('registered_user', 'unregistered_user', 'org_member'))
            """))
            
            self.session.commit()
            print("   ✅ Role column added successfully")
            
        except SQLAlchemyError as e:
            self.session.rollback()
            # Check if column already exists
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print("   ℹ️  Role column already exists, skipping...")
            else:
                raise
    
    def backfill_role_data(self) -> List[Tuple[int, str, str]]:
        """Backfill role data based on user profile analysis.
        
        Returns:
            List of (user_id, old_classification, new_role) tuples
        """
        print("🔄 Backfilling role data based on profile analysis...")
        
        updates = []
        users = self.session.query(User).all()
        
        for user in users:
            # Determine role based on current logic
            computed_role = user.get_role()
            
            # Log the classification reasoning
            if user.email and user.email.strip():
                if user.email.endswith('@tournamentorg.com') or user.email.endswith('@admin.com'):
                    old_classification = "admin/org_member"
                else:
                    old_classification = "member (has email)"
            else:
                old_classification = "non-member (no email)"
            
            updates.append((user.id, old_classification, computed_role.value))
            
            if not self.dry_run:
                # Update the role column directly
                self.session.execute(
                    text("UPDATE users SET role = :role WHERE id = :user_id"),
                    {"role": computed_role.value, "user_id": user.id}
                )
        
        if not self.dry_run:
            self.session.commit()
            print(f"   ✅ Updated {len(updates)} users with role data")
        else:
            print(f"   [DRY RUN] Would update {len(updates)} users")
            
        return updates
    
    def create_performance_index(self) -> None:
        """Create composite index for role-based queries."""
        print("📊 Creating performance index for role queries...")
        
        if self.dry_run:
            print("   [DRY RUN] Would create index: CREATE INDEX idx_users_role_created ON users(role, created_at)")
            return
            
        try:
            self.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_users_role_created 
                ON users(role, created_at)
            """))
            self.session.commit()
            print("   ✅ Performance index created")
            
        except SQLAlchemyError as e:
            self.session.rollback()
            if "already exists" in str(e).lower():
                print("   ℹ️  Index already exists, skipping...")
            else:
                raise
    
    def remove_legacy_column(self) -> None:
        """Remove legacy is_member column if it exists."""
        print("🗑️  Removing legacy is_member column...")
        
        inspector = inspect(self.session.bind)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'is_member' not in columns:
            print("   ℹ️  Legacy is_member column doesn't exist, skipping...")
            return
            
        if self.dry_run:
            print("   [DRY RUN] Would execute: ALTER TABLE users DROP COLUMN is_member")
            return
            
        try:
            self.session.execute(text("ALTER TABLE users DROP COLUMN is_member"))
            self.session.commit() 
            print("   ✅ Legacy column removed")
            
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"   ⚠️  Could not remove legacy column: {e}")
            print("      This may need to be done manually after ensuring no code dependencies remain")
    
    def verify_migration(self) -> bool:
        """Verify migration completed successfully.
        
        Returns:
            bool: True if migration is valid
        """
        print("🔍 Verifying migration...")
        
        try:
            # Check that all users have valid roles
            invalid_roles = self.session.execute(text("""
                SELECT id, role FROM users 
                WHERE role NOT IN ('registered_user', 'unregistered_user', 'org_member')
                OR role IS NULL
            """)).fetchall()
            
            if invalid_roles:
                print(f"   ❌ Found {len(invalid_roles)} users with invalid roles:")
                for user_id, role in invalid_roles:
                    print(f"      User {user_id}: '{role}'")
                return False
            
            # Check role distribution makes sense
            role_counts = {}
            for role in ['registered_user', 'unregistered_user', 'org_member']:
                count = self.session.execute(
                    text("SELECT COUNT(*) FROM users WHERE role = :role"),
                    {"role": role}
                ).scalar()
                role_counts[role] = count
            
            print("   ✅ Migration verification passed")
            print(f"      Role distribution: {role_counts}")
            return True
            
        except SQLAlchemyError as e:
            print(f"   ❌ Migration verification failed: {e}")
            return False
    
    def run_forward_migration(self) -> bool:
        """Run the complete forward migration.
        
        Returns:
            bool: True if successful
        """
        print(f"🚀 Starting role terminology migration {'(DRY RUN)' if self.dry_run else ''}")
        print(f"   Timestamp: {datetime.now().isoformat()}")
        
        try:
            # Check current status
            status = self.check_migration_status()
            print(f"\n📊 Current Status:")
            print(f"   Total users: {status['total_users']}")
            print(f"   Has role column: {status['has_role_column']}")
            print(f"   Has legacy is_member column: {status['has_is_member_column']}")
            print(f"   Current role distribution: {status['role_distribution']}")
            
            if not status['migration_needed']:
                print("\n✅ Migration already completed!")
                return True
            
            # Step 1: Add role column
            if not status['has_role_column']:
                self.add_role_column()
            
            # Step 2: Backfill data  
            updates = self.backfill_role_data()
            
            # Step 3: Create performance index
            self.create_performance_index()
            
            # Step 4: Verify migration
            if not self.dry_run:
                if not self.verify_migration():
                    return False
            
            print(f"\n🎉 Migration completed successfully!")
            
            if updates:
                print(f"\n📋 Migration Summary:")
                for user_id, old_class, new_role in updates[:10]:  # Show first 10
                    print(f"   User {user_id}: {old_class} → {new_role}")
                if len(updates) > 10:
                    print(f"   ... and {len(updates) - 10} more users")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            if not self.dry_run:
                self.session.rollback()
            return False
    
    def run_reverse_migration(self) -> bool:
        """Run reverse migration (for rollback).
        
        Returns:
            bool: True if successful
        """
        print(f"🔄 Starting reverse migration {'(DRY RUN)' if self.dry_run else ''}")
        
        try:
            # This is a destructive operation - require explicit confirmation
            if not self.dry_run:
                response = input("⚠️  This will remove the role column and data. Continue? (yes/no): ")
                if response.lower() != 'yes':
                    print("❌ Reverse migration cancelled")
                    return False
            
            # Remove role column and index
            if self.dry_run:
                print("   [DRY RUN] Would drop index and role column")
            else:
                try:
                    self.session.execute(text("DROP INDEX IF EXISTS idx_users_role_created"))
                    self.session.execute(text("ALTER TABLE users DROP COLUMN role"))
                    self.session.commit()
                    print("   ✅ Role column and index removed")
                except SQLAlchemyError as e:
                    print(f"   ⚠️  Partial rollback: {e}")
            
            print("🎉 Reverse migration completed")
            return True
            
        except Exception as e:
            print(f"❌ Reverse migration failed: {e}")
            if not self.dry_run:
                self.session.rollback()
            return False


def main():
    """Main migration script entry point."""
    parser = argparse.ArgumentParser(description="Role terminology migration script")
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be done without making changes')
    parser.add_argument('--reverse', action='store_true',
                       help='Reverse the migration (remove role column)')
    parser.add_argument('--status', action='store_true',
                       help='Show current migration status only')
    
    args = parser.parse_args()
    
    # Initialize database
    db_manager.create_tables()
    
    try:
        with RoleTerminologyMigration(dry_run=args.dry_run) as migration:
            
            if args.status:
                status = migration.check_migration_status()
                print("📊 Migration Status:")
                print(f"   Total users: {status['total_users']}")
                print(f"   Has role column: {status['has_role_column']}")
                print(f"   Has legacy column: {status['has_is_member_column']}")
                print(f"   Migration needed: {status['migration_needed']}")
                print(f"   Role distribution: {status['role_distribution']}")
                return 0
            
            if args.reverse:
                success = migration.run_reverse_migration()
            else:
                success = migration.run_forward_migration()
            
            return 0 if success else 1
            
    except KeyboardInterrupt:
        print("\n🛑 Migration interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())