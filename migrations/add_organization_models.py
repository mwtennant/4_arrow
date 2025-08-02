"""Database migration script for organization data models.

This migration adds the four new tables required for organization membership,
roles, permissions, and their relationships:
- permissions
- roles  
- role_permissions
- organization_memberships

Revision ID: org_data_models_001
Revises: base
Create Date: 2025-01-XX XX:XX:XX.XXXXXX
"""

from typing import Dict, Any, List, Tuple
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, Boolean, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from storage.database import DatabaseManager


class OrganizationModelsMessageMigration:
    """Migration class for adding organization data models."""
    
    def __init__(self, dry_run: bool = True):
        """Initialize migration.
        
        Args:
            dry_run: If True, perform validation without making changes
        """
        self.dry_run = dry_run
        self.db_manager = DatabaseManager()
        self.session = None
        
    def __enter__(self):
        """Context manager entry."""
        self.session = self.db_manager.get_session()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        if self.session:
            if exc_type:
                self.session.rollback()
            self.session.close()
    
    def check_migration_status(self) -> Dict[str, Any]:
        """Check current migration status.
        
        Returns:
            Dictionary containing migration status information
        """
        metadata = MetaData()
        metadata.reflect(bind=self.session.bind)
        
        existing_tables = metadata.tables.keys()
        
        # Check which tables already exist
        required_tables = ['permissions', 'roles', 'role_permissions', 'organization_memberships']
        existing_required = [table for table in required_tables if table in existing_tables]
        
        # Check if organizations and users tables exist (prerequisites)
        has_prerequisites = 'organizations' in existing_tables and 'users' in existing_tables
        
        status = {
            'has_prerequisites': has_prerequisites,
            'existing_required_tables': existing_required,
            'missing_tables': [t for t in required_tables if t not in existing_required],
            'migration_needed': len(existing_required) < len(required_tables),
            'can_migrate': has_prerequisites and len(existing_required) == 0,
            'existing_tables': list(existing_tables)
        }
        
        # If tables exist, check their structure
        if existing_required:
            status['table_structures'] = {}
            for table_name in existing_required:
                table = metadata.tables[table_name]
                status['table_structures'][table_name] = {
                    'columns': [col.name for col in table.columns],
                    'constraints': [str(constraint) for constraint in table.constraints],
                    'indexes': [idx.name for idx in table.indexes]
                }
        
        return status
    
    def create_permissions_table(self) -> bool:
        """Create the permissions table.
        
        Returns:
            True if successful, False otherwise
        """
        create_sql = text("""
            CREATE TABLE permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(64) NOT NULL,
                description VARCHAR(255),
                organization_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (organization_id) REFERENCES organizations(id),
                CONSTRAINT uq_permission_name_org UNIQUE (name, organization_id)
            )
        """)
        
        index_sql = text("""
            CREATE INDEX ix_permission_org_name ON permissions (organization_id, name)
        """)
        
        if self.dry_run:
            print("DRY RUN: Would execute:")
            print(str(create_sql))
            print(str(index_sql))
            return True
        
        try:
            self.session.execute(create_sql)
            self.session.execute(index_sql)
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error creating permissions table: {e}")
            self.session.rollback()
            return False
    
    def create_roles_table(self) -> bool:
        """Create the roles table.
        
        Returns:
            True if successful, False otherwise
        """
        create_sql = text("""
            CREATE TABLE roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(64) NOT NULL,
                organization_id INTEGER NOT NULL,
                parent_role_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (organization_id) REFERENCES organizations(id),
                FOREIGN KEY (parent_role_id) REFERENCES roles(id),
                CONSTRAINT uq_role_name_org UNIQUE (name, organization_id)
            )
        """)
        
        index_sql = text("""
            CREATE INDEX ix_role_org_name ON roles (organization_id, name)
        """)
        
        if self.dry_run:
            print("DRY RUN: Would execute:")
            print(str(create_sql))
            print(str(index_sql))
            return True
        
        try:
            self.session.execute(create_sql)
            self.session.execute(index_sql)
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error creating roles table: {e}")
            self.session.rollback()
            return False
    
    def create_role_permissions_table(self) -> bool:
        """Create the role_permissions association table.
        
        Returns:
            True if successful, False otherwise
        """
        create_sql = text("""
            CREATE TABLE role_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_id INTEGER NOT NULL,
                permission_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (role_id) REFERENCES roles(id),
                FOREIGN KEY (permission_id) REFERENCES permissions(id),
                CONSTRAINT uq_role_permission UNIQUE (role_id, permission_id)
            )
        """)
        
        indexes_sql = [
            text("CREATE INDEX ix_role_permission_role ON role_permissions (role_id)"),
            text("CREATE INDEX ix_role_permission_permission ON role_permissions (permission_id)"),
        ]
        
        if self.dry_run:
            print("DRY RUN: Would execute:")
            print(str(create_sql))
            for idx_sql in indexes_sql:
                print(str(idx_sql))
            return True
        
        try:
            self.session.execute(create_sql)
            for idx_sql in indexes_sql:
                self.session.execute(idx_sql)
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error creating role_permissions table: {e}")
            self.session.rollback()
            return False
    
    def create_organization_memberships_table(self) -> bool:
        """Create the organization_memberships table.
        
        Returns:
            True if successful, False otherwise
        """
        create_sql = text("""
            CREATE TABLE organization_memberships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                organization_id INTEGER NOT NULL,
                role_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (organization_id) REFERENCES organizations(id),
                FOREIGN KEY (role_id) REFERENCES roles(id),
                CONSTRAINT uq_user_organization UNIQUE (user_id, organization_id)
            )
        """)
        
        indexes_sql = [
            text("CREATE INDEX ix_membership_user ON organization_memberships (user_id)"),
            text("CREATE INDEX ix_membership_org ON organization_memberships (organization_id)"),
            text("CREATE INDEX ix_membership_role ON organization_memberships (role_id)"),
        ]
        
        if self.dry_run:
            print("DRY RUN: Would execute:")
            print(str(create_sql))
            for idx_sql in indexes_sql:
                print(str(idx_sql))
            return True
        
        try:
            self.session.execute(create_sql)
            for idx_sql in indexes_sql:
                self.session.execute(idx_sql)
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error creating organization_memberships table: {e}")
            self.session.rollback()
            return False
    
    def create_sample_data(self) -> bool:
        """Create sample permissions and roles for testing.
        
        Returns:
            True if successful, False otherwise
        """
        if self.dry_run:
            print("DRY RUN: Would create sample data")
            return True
        
        # Check if we have at least one organization
        org_count = self.session.execute(text("SELECT COUNT(*) FROM organizations")).scalar()
        if org_count == 0:
            print("No organizations found, skipping sample data creation")
            return True
        
        # Get first organization
        org_id = self.session.execute(text("SELECT id FROM organizations LIMIT 1")).scalar()
        
        sample_data = [
            # Sample permissions
            text("INSERT OR IGNORE INTO permissions (name, description, organization_id) VALUES ('manage_tournaments', 'Can create and manage tournaments', :org_id)"),
            text("INSERT OR IGNORE INTO permissions (name, description, organization_id) VALUES ('view_reports', 'Can view tournament reports', :org_id)"),
            text("INSERT OR IGNORE INTO permissions (name, description, organization_id) VALUES ('manage_members', 'Can manage organization members', :org_id)"),
            text("INSERT OR IGNORE INTO permissions (name, description, organization_id) VALUES ('admin_access', 'Full administrative access', :org_id)"),
            
            # Sample roles
            text("INSERT OR IGNORE INTO roles (name, organization_id) VALUES ('Tournament Manager', :org_id)"),
            text("INSERT OR IGNORE INTO roles (name, organization_id) VALUES ('Administrator', :org_id)"),
            text("INSERT OR IGNORE INTO roles (name, organization_id) VALUES ('Member', :org_id)"),
        ]
        
        try:
            for sql in sample_data:
                self.session.execute(sql, {'org_id': org_id})
            self.session.commit()
            
            print(f"Created sample data for organization ID {org_id}")
            return True
        except Exception as e:
            print(f"Error creating sample data: {e}")
            self.session.rollback()
            return False
    
    def verify_migration(self) -> bool:
        """Verify the migration was successful.
        
        Returns:
            True if migration is verified successful
        """
        try:
            # Check all tables exist
            required_tables = ['permissions', 'roles', 'role_permissions', 'organization_memberships']
            
            for table in required_tables:
                result = self.session.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")).fetchone()
                if not result:
                    print(f"Table {table} not found")
                    return False
            
            # Check table structures
            checks = [
                ("permissions", "SELECT id, name, organization_id FROM permissions LIMIT 1"),
                ("roles", "SELECT id, name, organization_id, parent_role_id FROM roles LIMIT 1"),
                ("role_permissions", "SELECT id, role_id, permission_id FROM role_permissions LIMIT 1"),
                ("organization_memberships", "SELECT id, user_id, organization_id, role_id FROM organization_memberships LIMIT 1"),
            ]
            
            for table_name, check_sql in checks:
                try:
                    self.session.execute(text(check_sql))
                except Exception as e:
                    print(f"Structure check failed for {table_name}: {e}")
                    return False
            
            print("Migration verification successful")
            return True
            
        except Exception as e:
            print(f"Migration verification failed: {e}")
            return False
    
    def run_forward_migration(self) -> bool:
        """Run the complete forward migration.
        
        Returns:
            True if migration successful
        """
        print("Starting organization data models migration...")
        
        # Check migration status
        status = self.check_migration_status()
        
        print(f"Migration status check:")
        print(f"  Prerequisites available: {status['has_prerequisites']}")
        print(f"  Can migrate: {status['can_migrate']}")
        print(f"  Missing tables: {status['missing_tables']}")
        
        if not status['has_prerequisites']:
            print("ERROR: Missing prerequisite tables (users, organizations)")
            return False
        
        if not status['migration_needed']:
            print("Migration not needed - all tables already exist")
            return True
        
        if not status['can_migrate']:
            print("ERROR: Cannot migrate - some tables already exist")
            return False
        
        # Execute migration steps
        steps = [
            ("Creating permissions table", self.create_permissions_table),
            ("Creating roles table", self.create_roles_table),
            ("Creating role_permissions table", self.create_role_permissions_table),
            ("Creating organization_memberships table", self.create_organization_memberships_table),
            ("Creating sample data", self.create_sample_data),
        ]
        
        for step_name, step_func in steps:
            print(f"Executing: {step_name}")
            if not step_func():
                print(f"FAILED: {step_name}")
                return False
            print(f"SUCCESS: {step_name}")
        
        # Verify migration
        if not self.verify_migration():
            print("FAILED: Migration verification")
            return False
        
        print("Organization data models migration completed successfully!")
        return True
    
    def run_reverse_migration(self) -> bool:
        """Run reverse migration (drop tables).
        
        Returns:
            True if reverse migration successful
        """
        print("Starting reverse migration...")
        
        # Tables to drop in reverse order (respecting foreign keys)
        tables_to_drop = [
            'organization_memberships',
            'role_permissions', 
            'roles',
            'permissions'
        ]
        
        if self.dry_run:
            print("DRY RUN: Would drop tables in order:")
            for table in tables_to_drop:
                print(f"  DROP TABLE IF EXISTS {table}")
            return True
        
        try:
            for table in tables_to_drop:
                drop_sql = text(f"DROP TABLE IF EXISTS {table}")
                self.session.execute(drop_sql)
                print(f"Dropped table: {table}")
            
            self.session.commit()
            print("Reverse migration completed successfully!")
            return True
            
        except Exception as e:
            print(f"Reverse migration failed: {e}")
            self.session.rollback()
            return False


def main():
    """Main function to run migration."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Organization data models migration')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    parser.add_argument('--reverse', action='store_true', help='Run reverse migration (drop tables)')
    parser.add_argument('--status', action='store_true', help='Show migration status only')
    
    args = parser.parse_args()
    
    try:
        with OrganizationModelsMessageMigration(dry_run=args.dry_run) as migration:
            if args.status:
                status = migration.check_migration_status()
                print("Migration Status:")
                for key, value in status.items():
                    print(f"  {key}: {value}")
                return
            
            if args.reverse:
                success = migration.run_reverse_migration()
            else:
                success = migration.run_forward_migration()
            
            if success:
                print("Migration completed successfully")
            else:
                print("Migration failed")
                exit(1)
                
    except Exception as e:
        print(f"Migration error: {e}")
        exit(1)


if __name__ == '__main__':
    main()