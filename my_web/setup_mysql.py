#!/usr/bin/env python3
"""
MySQL Database Setup Script for Shop App

This script creates the MySQL database and tables for the shop application.
Make sure MySQL is running and you have the correct credentials.

Usage:
1. Install MySQL and start the service
2. Create a database user with privileges
3. Set environment variables or edit this script
4. Run: python setup_mysql.py
"""

import pymysql
import os
from pathlib import Path

# Database configuration - EDIT THESE VALUES
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "shop_db")

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect without specifying database
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4'
        )
        c = conn.cursor()

        # Create database
        c.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"[OK] Database '{DB_NAME}' created or already exists")

        conn.commit()
        conn.close()
        return True

    except pymysql.Error as e:
        print(f"[ERROR] Error creating database: {e}")
        return False

def setup_tables():
    """Create all tables"""
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        c = conn.cursor()

        # Products table
        c.execute('''CREATE TABLE IF NOT EXISTS products (
                     id INT AUTO_INCREMENT PRIMARY KEY,
                     name VARCHAR(255) NOT NULL,
                     price INT NOT NULL,
                     image VARCHAR(500),
                     category VARCHAR(100),
                     description TEXT,
                     stock INT DEFAULT 0,
                     seller VARCHAR(100),
                     source VARCHAR(50),
                     purchaseLimit INT DEFAULT 1
                     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                     id INT AUTO_INCREMENT PRIMARY KEY,
                     username VARCHAR(100) UNIQUE NOT NULL,
                     password VARCHAR(255) NOT NULL
                     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

        # Admins table
        c.execute('''CREATE TABLE IF NOT EXISTS admins (
                     id INT AUTO_INCREMENT PRIMARY KEY,
                     username VARCHAR(100) UNIQUE NOT NULL,
                     password VARCHAR(255) NOT NULL,
                     isAdmin TINYINT DEFAULT 0
                     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

        # Cart table
        c.execute('''CREATE TABLE IF NOT EXISTS cart (
                     id INT AUTO_INCREMENT PRIMARY KEY,
                     data JSON,
                     user_id VARCHAR(100)
                     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

        # Bought products table
        c.execute('''CREATE TABLE IF NOT EXISTS bought_products (
                     id INT AUTO_INCREMENT PRIMARY KEY,
                     user VARCHAR(100),
                     userId VARCHAR(100),
                     email VARCHAR(255),
                     orderNumber INT,
                     product JSON,
                     timestamp VARCHAR(50)
                     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

        # Comments table
        c.execute('''CREATE TABLE IF NOT EXISTS comments (
                     id INT AUTO_INCREMENT PRIMARY KEY,
                     user VARCHAR(100) NOT NULL,
                     product INT NOT NULL,
                     text TEXT NOT NULL,
                     timestamp VARCHAR(50),
                     edited TINYINT DEFAULT 0
                     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

        # Ratings table
        c.execute('''CREATE TABLE IF NOT EXISTS ratings (
                     id INT AUTO_INCREMENT PRIMARY KEY,
                     productId INT NOT NULL,
                     user VARCHAR(100) NOT NULL,
                     value INT NOT NULL
                     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

        # Views table
        c.execute('''CREATE TABLE IF NOT EXISTS views (
                     id INT AUTO_INCREMENT PRIMARY KEY,
                     productId INT NOT NULL,
                     view_count INT DEFAULT 0
                     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

        # Favored table
        c.execute('''CREATE TABLE IF NOT EXISTS favored (
                     id INT AUTO_INCREMENT PRIMARY KEY,
                     productId INT NOT NULL,
                     total INT DEFAULT 0,
                     byUser JSON
                     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

        conn.commit()
        conn.close()
        print("[OK] All tables created successfully")
        return True

    except pymysql.Error as e:
        print(f"[ERROR] Error creating tables: {e}")
        return False

def test_connection():
    """Test database connection"""
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        conn.close()
        print("[OK] Database connection successful")
        return True
    except pymysql.Error as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("MySQL Database Setup for Shop App")
    print("=" * 40)

    print(f"Host: {DB_HOST}")
    print(f"User: {DB_USER}")
    print(f"Database: {DB_NAME}")
    print()

    print("Setting up database...")

    if create_database():
        if setup_tables():
            if test_connection():
                print("\n[SUCCESS] Setup completed successfully!")
                print("\nNext steps:")
                print("1. Set environment variables or update app.py with your MySQL credentials")
                print("2. Run: python app.py")
            else:
                print("\n[ERROR] Setup failed - check your MySQL configuration")
        else:
            print("\n[ERROR] Failed to create tables")
    else:
        print("\n[ERROR] Failed to create database")