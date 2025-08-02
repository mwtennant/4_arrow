-- Database schema enhancements for merge profiles functionality
-- Add unique indexes and constraints for better data integrity

-- Add deleted_at column if it doesn't exist (for soft delete functionality)
-- Note: This should be handled by SQLAlchemy migrations in practice
-- ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP NULL;

-- Create index on deleted_at for efficient queries on active users
CREATE INDEX IF NOT EXISTS idx_users_deleted_at ON users(deleted_at) 
WHERE deleted_at IS NOT NULL;

-- Create composite unique index on email and phone for active users only
-- This prevents duplicate email+phone combinations among non-deleted users
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_phone_active ON users(email, phone) 
WHERE deleted_at IS NULL AND email IS NOT NULL AND phone IS NOT NULL;

-- Index for efficient lookups by USBC ID among active users
CREATE INDEX IF NOT EXISTS idx_users_usbc_id_active ON users(usbc_id) 
WHERE deleted_at IS NULL AND usbc_id IS NOT NULL;

-- Index for efficient lookups by TNBA ID among active users  
CREATE INDEX IF NOT EXISTS idx_users_tnba_id_active ON users(tnba_id)
WHERE deleted_at IS NULL AND tnba_id IS NOT NULL;

-- Composite index for name-based searches among active users
CREATE INDEX IF NOT EXISTS idx_users_names_active ON users(last_name, first_name)
WHERE deleted_at IS NULL;