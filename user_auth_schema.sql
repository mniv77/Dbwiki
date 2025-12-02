# HaGOLEM Wiki - Multi-User Authentication System
# Add this to your existing database

# ============================================================================
# Users Table - Track who's using the system
# ============================================================================

CREATE TABLE hagolem_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- User credentials
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- Encrypted password
    
    -- User profile
    full_name VARCHAR(200),
    role VARCHAR(50) DEFAULT 'user',  -- 'admin', 'user', 'viewer'
    company VARCHAR(200),
    title VARCHAR(200),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    date_registered DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    
    -- Preferences
    notifications_enabled BOOLEAN DEFAULT TRUE,
    
    -- Indexes
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
);

# ============================================================================
# Update Existing Tables to Track Users
# ============================================================================

-- Add user tracking to ideas table
ALTER TABLE hagolem_ideas 
ADD COLUMN created_by_user_id INT,
ADD COLUMN modified_by_user_id INT,
ADD FOREIGN KEY (created_by_user_id) REFERENCES hagolem_users(id),
ADD FOREIGN KEY (modified_by_user_id) REFERENCES hagolem_users(id);

-- Add user tracking to comments table
ALTER TABLE hagolem_comments
ADD COLUMN user_id INT,
ADD FOREIGN KEY (user_id) REFERENCES hagolem_users(id);

-- Update history table to track users
ALTER TABLE hagolem_history
ADD COLUMN user_id INT,
ADD FOREIGN KEY (user_id) REFERENCES hagolem_users(id);

# ============================================================================
# Session Table - Track who's logged in
# ============================================================================

CREATE TABLE hagolem_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(50),
    user_agent TEXT,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES hagolem_users(id) ON DELETE CASCADE,
    INDEX idx_token (session_token),
    INDEX idx_user (user_id),
    INDEX idx_expires (expires_at)
);

# ============================================================================
# Activity Log - Track all user actions
# ============================================================================

CREATE TABLE hagolem_activity_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100),  -- 'login', 'view_idea', 'add_comment', 'edit_idea', etc.
    target_type VARCHAR(50),  -- 'idea', 'comment', 'user', etc.
    target_id INT,
    details TEXT,  -- JSON with additional info
    ip_address VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES hagolem_users(id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_action (action),
    INDEX idx_date (created_at)
);

# ============================================================================
# Create First Admin User (YOU, Meir)
# ============================================================================

-- Password is 'hagolem123' - CHANGE THIS AFTER FIRST LOGIN!
-- Hash generated with bcrypt
INSERT INTO hagolem_users 
(username, email, password_hash, full_name, role, is_active, email_verified)
VALUES 
('meir', 'meir@hagolem.com', '$2b$12$LQ3Z5X8Y9J4K6M7N8P9Q0.abcdefghijklmnopqrstuvwxyz123456', 
 'Meir Nivgad', 'admin', TRUE, TRUE);

-- Note: You'll need to generate a real password hash using bcrypt in Python
-- The above is just a placeholder format

# ============================================================================
# Useful Queries for Multi-User System
# ============================================================================

-- Get all users
-- SELECT id, username, full_name, email, role, last_login FROM hagolem_users ORDER BY date_registered DESC;

-- Get user activity
-- SELECT * FROM hagolem_activity_log WHERE user_id = ? ORDER BY created_at DESC LIMIT 50;

-- Get ideas by user
-- SELECT * FROM hagolem_ideas WHERE created_by_user_id = ? ORDER BY date_created DESC;

-- Get most active users (by comments)
-- SELECT u.username, u.full_name, COUNT(c.id) as comment_count
-- FROM hagolem_users u
-- LEFT JOIN hagolem_comments c ON u.id = c.user_id
-- GROUP BY u.id
-- ORDER BY comment_count DESC;

-- Clean up expired sessions (run periodically)
-- DELETE FROM hagolem_sessions WHERE expires_at < NOW();
