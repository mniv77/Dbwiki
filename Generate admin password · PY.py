#!/usr/bin/env python3
# Generate Password Hash for First Admin User
# Run this to create a password hash for your admin account

import bcrypt
import getpass

print("="*60)
print("HaGOLEM Wiki - Admin Password Hash Generator")
print("="*60)
print()

# Get password from user
password = getpass.getpass("Enter password for admin account: ")
confirm = getpass.getpass("Confirm password: ")

if password != confirm:
    print("\n❌ Passwords don't match!")
    exit(1)

if len(password) < 6:
    print("\n❌ Password must be at least 6 characters!")
    exit(1)

# Generate hash
print("\n⏳ Generating secure hash...")
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
hash_string = password_hash.decode('utf-8')

print("\n✅ Hash generated successfully!")
print("\n" + "="*60)
print("COPY THIS HASH:")
print("="*60)
print(hash_string)
print("="*60)

print("\nNow run this SQL command in MySQL console:")
print("\nUPDATE hagolem_users")
print(f"SET password_hash = '{hash_string}'")
print("WHERE username = 'meir';")
print()

print("Or create new admin user:")
print("\nINSERT INTO hagolem_users")
print("(username, email, password_hash, full_name, role, is_active, email_verified)")
print("VALUES")
print(f"('meir', 'your-email@example.com', '{hash_string}', 'Meir Nivgad', 'admin', TRUE, TRUE);")
print()

print("="*60)
print("✅ Done! Use the SQL command above to set your password.")
print("="*60)