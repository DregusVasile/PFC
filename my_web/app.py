from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pymysql
import os
import random
from datetime import datetime
import json
import sqlite3

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# =========================
# DATABASE SETUP
# =========================
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "shop_db")

# Fallback to SQLite if MySQL is not available
USE_SQLITE_FALLBACK = False
SQLITE_DB_PATH = "shop.db"

def init_db():
    """Initialize database - try MySQL first, fallback to SQLite"""
    global USE_SQLITE_FALLBACK
    
    try:
        # Try MySQL first
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
                     )''')
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                     id INT AUTO_INCREMENT PRIMARY KEY,
                     username VARCHAR(100) UNIQUE NOT NULL,
                     password VARCHAR(255) NOT NULL
                     )''')
        
        # Admins table
        c.execute('''CREATE TABLE IF NOT EXISTS admins (
                     id INT AUTO_INCREMENT PRIMARY KEY,
                     username VARCHAR(100) UNIQUE NOT NULL,
                     password VARCHAR(255) NOT NULL,
                     isAdmin TINYINT DEFAULT 0
                     )''')
        
        # Cart table
        c.execute('''CREATE TABLE IF NOT EXISTS cart (
                     id INT AUTO_INCREMENT PRIMARY KEY,
                     data JSON,
                     user_id VARCHAR(100)
                     )''')
        
        # Bought products table
        c.execute('''CREATE TABLE IF NOT EXISTS bought_products (
                     id INT AUTO_INCREMENT PRIMARY KEY,
                     user VARCHAR(100),
                     userId VARCHAR(100),
                     email VARCHAR(255),
                     orderNumber INT,
                     product JSON,
                     timestamp VARCHAR(50)
                     )''')
        
        # Comments table
        c.execute('''CREATE TABLE IF NOT EXISTS comments (
                     id INT AUTO_INCREMENT PRIMARY KEY,
                     user VARCHAR(100) NOT NULL,
                     product INT NOT NULL,
                     text TEXT NOT NULL,
                     timestamp VARCHAR(50),
                     edited TINYINT DEFAULT 0
                     )''')
        
        # Ratings table
        c.execute('''CREATE TABLE IF NOT EXISTS ratings (
                     id INT AUTO_INCREMENT PRIMARY KEY,
                     productId INT NOT NULL,
                     user VARCHAR(100) NOT NULL,
                     value INT NOT NULL
                     )''')
        
        # Views table
        c.execute('''CREATE TABLE IF NOT EXISTS views (
                     id INT AUTO_INCREMENT PRIMARY KEY,
                     productId INT NOT NULL,
                     view_count INT DEFAULT 0
                     )''')
        
        # Favored table
        c.execute('''CREATE TABLE IF NOT EXISTS favored (
                     id INT AUTO_INCREMENT PRIMARY KEY,
                     productId INT NOT NULL,
                     total INT DEFAULT 0,
                     byUser JSON
                     )''')
        
        conn.commit()
        conn.close()
        print("Database initialized with MySQL")
        USE_SQLITE_FALLBACK = False
        
    except Exception as e:
        print(f"MySQL not available ({e}), using SQLite fallback")
        USE_SQLITE_FALLBACK = True
        # Initialize SQLite database
        conn = sqlite3.connect(SQLITE_DB_PATH)
        c = conn.cursor()
        
        # Products table
        c.execute('''CREATE TABLE IF NOT EXISTS products (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     price INTEGER NOT NULL,
                     image TEXT,
                     category TEXT,
                     description TEXT,
                     stock INTEGER DEFAULT 0,
                     seller TEXT,
                     source TEXT,
                     purchaseLimit INTEGER DEFAULT 1
                     )''')
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT UNIQUE NOT NULL,
                     password TEXT NOT NULL
                     )''')
        
        # Admins table
        c.execute('''CREATE TABLE IF NOT EXISTS admins (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT UNIQUE NOT NULL,
                     password TEXT NOT NULL,
                     isAdmin INTEGER DEFAULT 0
                     )''')
        
        # Cart table
        c.execute('''CREATE TABLE IF NOT EXISTS cart (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     data TEXT,
                     user_id TEXT
                     )''')
        
        # Bought products table
        c.execute('''CREATE TABLE IF NOT EXISTS bought_products (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user TEXT,
                     userId TEXT,
                     email TEXT,
                     orderNumber INTEGER,
                     product TEXT,
                     timestamp TEXT
                     )''')
        
        # Comments table
        c.execute('''CREATE TABLE IF NOT EXISTS comments (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user TEXT NOT NULL,
                     product INTEGER NOT NULL,
                     text TEXT NOT NULL,
                     timestamp TEXT,
                     edited INTEGER DEFAULT 0
                     )''')
        
        # Ratings table
        c.execute('''CREATE TABLE IF NOT EXISTS ratings (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     productId INTEGER NOT NULL,
                     user TEXT NOT NULL,
                     value INTEGER NOT NULL
                     )''')
        
        # Views table
        c.execute('''CREATE TABLE IF NOT EXISTS views (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     productId INTEGER NOT NULL,
                     view_count INTEGER DEFAULT 0
                     )''')
        
        # Favored table
        c.execute('''CREATE TABLE IF NOT EXISTS favored (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     productId INTEGER NOT NULL,
                     total INTEGER DEFAULT 0,
                     byUser TEXT
                     )''')
        
        conn.commit()
        conn.close()
        print("Database initialized with SQLite")
init_db()



# =========================
# JSON → MySQL MIGRATION
# =========================
def _load_json(path, default=None):
    if default is None:
        default = []
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def migrate_data():
    conn = get_db()
    c = conn.cursor()

    # Products
    c.execute("SELECT COUNT(*) as cnt FROM products")
    if c.fetchone()["cnt"] == 0:
        products = _load_json(os.path.join(os.path.dirname(__file__), "products.json"))
        for p in products:
            c.execute('''INSERT OR IGNORE INTO products
                         (id, name, price, image, category, description, stock, seller, source, purchaseLimit)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (p.get("id"), p.get("name"), p.get("price", 0), p.get("image", ""),
                       p.get("category", ""), p.get("description", ""), p.get("stock", 0),
                       p.get("seller", "Shop"), "shop", p.get("purchaseLimit", 1)))

        my_products = _load_json(os.path.join(os.path.dirname(__file__), "myproducts.json"))
        for p in my_products:
            c.execute('''INSERT OR IGNORE INTO products
                         (id, name, price, image, category, description, stock, seller, source, purchaseLimit)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (p.get("id"), p.get("name"), p.get("price", 0), p.get("image", ""),
                       p.get("category", ""), p.get("description", ""), p.get("stock", 0),
                       p.get("seller", "Guest"), "my", p.get("purchaseLimit", 1)))

    # Users
    c.execute("SELECT COUNT(*) as cnt FROM users")
    if c.fetchone()["cnt"] == 0:
        users = _load_json(os.path.join(os.path.dirname(__file__), "users.json"))
        for u in users:
            c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
                      (u.get("username"), u.get("password")))

        admins = _load_json(os.path.join(os.path.dirname(__file__), "adminuser.json"))
        for a in admins:
            c.execute("INSERT OR IGNORE INTO admins (username, password, isAdmin) VALUES (?, ?, ?)",
                      (a.get("username"), a.get("password"), 1 if a.get("isAdmin") else 0))

    # Comments
    c.execute("SELECT COUNT(*) as cnt FROM comments")
    if c.fetchone()["cnt"] == 0:
        comments = _load_json(os.path.join(os.path.dirname(__file__), "comments.json"))
        for comment in comments:
            c.execute('''INSERT OR IGNORE INTO comments (id, user, product, text, timestamp, edited)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (comment.get("id"), comment.get("user"), comment.get("product"),
                       comment.get("text"), comment.get("timestamp", str(datetime.now())),
                       1 if comment.get("edited") else 0))

    # Ratings
    c.execute("SELECT COUNT(*) as cnt FROM ratings")
    if c.fetchone()["cnt"] == 0:
        ratings = _load_json(os.path.join(os.path.dirname(__file__), "rating.json"), {})
        for pid, rating_data in ratings.items():
            for user, value in rating_data.get("userRatings", {}).items():
                c.execute("INSERT OR IGNORE INTO ratings (productId, user, value) VALUES (?, ?, ?)",
                          (int(pid), user, value))

    # Views
    c.execute("SELECT COUNT(*) as cnt FROM views")
    if c.fetchone()["cnt"] == 0:
        views = _load_json(os.path.join(os.path.dirname(__file__), "views.json"), {})
        for pid, view_count in views.items():
            c.execute("INSERT OR IGNORE INTO views (productId, view_count) VALUES (?, ?)",
                      (int(pid), view_count))

    # Favored
    c.execute("SELECT COUNT(*) as cnt FROM favored")
    if c.fetchone()["cnt"] == 0:
        favored = _load_json(os.path.join(os.path.dirname(__file__), "favored.json"), {})
        for pid, item in favored.items():
            c.execute("INSERT OR IGNORE INTO favored (productId, total, byUser) VALUES (?, ?, ?)",
                      (int(pid), item.get("total", 0), json.dumps(item.get("byUser", {}))))

    # Bought products
    c.execute("SELECT COUNT(*) as cnt FROM bought_products")
    if c.fetchone()["cnt"] == 0:
        orders = _load_json(os.path.join(os.path.dirname(__file__), "boughtproducts.json"), [])
        for order in orders:
            c.execute('''INSERT OR IGNORE INTO bought_products
                         (user, userId, email, orderNumber, product, timestamp)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (order.get("user"), order.get("userId"), order.get("email"),
                       order.get("orderNumber"), json.dumps(order.get("product", {})),
                       order.get("timestamp", str(datetime.now()))))

    conn.commit()
    conn.close()

# migrate_data() will be called after get_db() is defined

def get_db():
    """Get database connection - MySQL or SQLite fallback"""
    global USE_SQLITE_FALLBACK
    
    if USE_SQLITE_FALLBACK:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row  # Make rows dict-like
        return conn
    try:
        return pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except:
        USE_SQLITE_FALLBACK = True
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

migrate_data()

# =========================
# PYDANTIC MODELS
# =========================
class ProductCreate(BaseModel):
    name: str
    price: int
    image: str
    category: str
    description: str
    stock: int
    seller: str
    purchaseLimit: int

class UserLogin(BaseModel):
    username: str
    password: str

class UserSignup(BaseModel):
    username: str
    password: str

class CartItem(BaseModel):
    product_id: int
    name: str
    price: int
    quantity: int
    source: str

class CommentData(BaseModel):
    user: str
    product: int
    text: str

class RatingData(BaseModel):
    productId: int
    user: str
    value: int

class BuyData(BaseModel):
    product: Dict[str, Any]
    quantity: int
    user: str
    email: str
    userId: str

# Mount static files
# =========================
# LOAD PRODUCTS JSON
# =========================
@app.get("/products-json")
def products_json():
    """Load products from database"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE source = 'shop'")
    rows = c.fetchall()
    conn.close()
    
    products = [dict(row) for row in rows]
    return JSONResponse(products)

@app.post("/add-product")
def add_product(product: ProductCreate):
    """Add new product"""
    conn = get_db()
    c = conn.cursor()
    
    price = product.price if product.price > 0 else 1
    stock = product.stock if product.stock >= 1 else 1
    purchase_limit = product.purchaseLimit if product.purchaseLimit >= 1 else 1
    
    c.execute('''INSERT INTO products 
                 (name, price, image, category, description, stock, seller, source, purchaseLimit)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (product.name, price, product.image, product.category, product.description,
               stock, product.seller, "my", purchase_limit))
    
    conn.commit()
    conn.close()
    
    return {"status": "ok"}

@app.get("/my-products-json")
def my_products_json():
    """Get user products"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE source = 'my'")
    rows = c.fetchall()
    conn.close()
    
    products = [dict(row) for row in rows]
    return JSONResponse(products)

@app.get("/all-products-json")
def all_products_json():
    """Get all products (shop + user)"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    rows = c.fetchall()
    conn.close()
    
    products = [dict(row) for row in rows]
    return JSONResponse(products)

@app.get("/categories")
def categories():
    """Get all categories"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != ''")
    rows = c.fetchall()
    conn.close()
    
    cats = sorted([row[0] for row in rows])
    return JSONResponse(cats)

@app.post("/buy-all")
def buy_all(data: BuyData):
    """Buy all - main purchase endpoint"""
    conn = get_db()
    c = conn.cursor()
    
    product = data.product
    quantity = max(1, data.quantity)
    product_id = product.get("product_id")
    source = product.get("source", "shop")

    if source == "my":
        # Check stock and purchase limit
        c.execute("SELECT stock, purchaseLimit FROM products WHERE id = ? AND source = 'my'", (product_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Product not found")
        
        stock = row["stock"]
        purchase_limit = row["purchaseLimit"]
        if quantity > stock:
            conn.close()
            raise HTTPException(status_code=400, detail="Nu mai sunt suficiente produse în stoc.")
        if quantity > purchase_limit:
            conn.close()
            raise HTTPException(status_code=400, detail=f"Limita de cumpărare este {purchase_limit} produse.")

        new_stock = stock - quantity
        if new_stock <= 0:
            c.execute("DELETE FROM products WHERE id = ? AND source = 'my'", (product_id,))
        else:
            c.execute("UPDATE products SET stock = ? WHERE id = ? AND source = 'my'", (new_stock, product_id))

    # Insert order
    product_json = json.dumps(product)
    c.execute("INSERT INTO bought_products (user, userId, email, orderNumber, product, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
              (data.user, data.userId, data.email, 0, product_json, str(datetime.now())))
    
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.post("/add-to-cart")
def add_to_cart(item: CartItem):
    """Add item to cart"""
    conn = get_db()
    c = conn.cursor()
    
    item_json = json.dumps(item.dict())
    c.execute("INSERT INTO cart (data, user_id) VALUES (?, ?)", (item_json, ""))
    
    conn.commit()
    conn.close()
    
    print(f"[SERVER] Added to cart: {item_json}")
    return {"status": "ok"}

@app.get("/get-cart")
def get_cart():
    """Get cart items"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT data FROM cart")
    rows = c.fetchall()
    conn.close()
    
    cart = [json.loads(row["data"]) for row in rows]
    print(f"[SERVER] get_cart returning: {cart}")
    return JSONResponse(cart)

@app.post("/remove-from-cart")
def remove_from_cart(data: Dict[str, Any]):
    """Remove item from cart by index"""
    conn = get_db()
    c = conn.cursor()
    
    index = data.get("index")
    
    try:
        index = int(index)
    except (TypeError, ValueError):
        conn.close()
        return {"status": "ok"}
    
    c.execute("SELECT id FROM cart LIMIT 1 OFFSET ?", (index,))
    row = c.fetchone()
    
    if row:
        c.execute("DELETE FROM cart WHERE id = ?", (row["id"],))
        conn.commit()
    
    conn.close()
    return {"status": "ok"}

@app.post("/clear-cart")
def clear_cart():
    """Clear all cart items"""
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM cart")
    conn.commit()
    conn.close()
    
    return {"status": "ok"}


# =========================
# LOGIN (users table)
# =========================
@app.post("/login")
def login(user: UserLogin):
    """Login user"""
    conn = get_db()
    c = conn.cursor()
    
    # Check in users table
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
              (user.username, user.password))
    found_user = c.fetchone()
    
    if found_user:
        # Clear user's cart
        c.execute("DELETE FROM cart")
        conn.commit()
        conn.close()
        return {"status": "ok", "isAdmin": False}
    
    # Check in admins table
    c.execute("SELECT * FROM admins WHERE username = ? AND password = ?", 
              (user.username, user.password))
    found_admin = c.fetchone()
    
    if found_admin:
        # Clear user's cart
        c.execute("DELETE FROM cart")
        conn.commit()
        conn.close()
        return {"status": "ok", "isAdmin": True}
    
    conn.close()
    return {"status": "fail"}

@app.post("/signup")
def signup(user: UserSignup):
    """Signup new user"""
    conn = get_db()
    c = conn.cursor()
    
    # Check if user exists
    c.execute("SELECT * FROM users WHERE username = ?", (user.username,))
    if c.fetchone():
        conn.close()
        return {"status": "exists"}
    
    # Add new user
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
              (user.username, user.password))
    
    # Clear cart
    c.execute("DELETE FROM cart")
    
    conn.commit()
    conn.close()
    
    return {"status": "ok"}

# =========================
# HELPER FUNCTIONS
# =========================
def is_admin(username):
    """Check if user is admin"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT isAdmin FROM admins WHERE username = ?", (username,))
    admin = c.fetchone()
    conn.close()
    return admin and admin[0] == 1

# =========================
# COMMENTS
# =========================
@app.get("/comments")
def get_comments():
    """Get all comments"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM comments")
    rows = c.fetchall()
    conn.close()
    
    comments = [dict(row) for row in rows]
    return JSONResponse(comments)

@app.post("/add-comment")
def add_comment(comment: CommentData):
    """Add new comment with 30 comment limit per user per product"""
    conn = get_db()
    c = conn.cursor()
    
    # Check limit - 30 comments per user per product
    c.execute("SELECT COUNT(*) as cnt FROM comments WHERE user = ? AND product = ?",
              (comment.user, comment.product))
    count = c.fetchone()["cnt"]
    
    if count >= 30:
        conn.close()
        return {"status": "limit"}
    
    # Add comment
    c.execute('''INSERT INTO comments (user, product, text, timestamp, edited)
                 VALUES (?, ?, ?, ?, ?)''',
              (comment.user, comment.product, comment.text, str(datetime.now()), 0))
    
    conn.commit()
    conn.close()
    
    return {"status": "ok"}

@app.post("/edit-comment")
def edit_comment(data: Dict[str, Any]):
    """Edit comment"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT * FROM comments WHERE id = ?", (data["id"],))
    comment = c.fetchone()
    
    if not comment:
        conn.close()
        return {"status": "not_found"}
    
    if comment["user"] == data["user"]:
        c.execute("UPDATE comments SET text = ?, edited = 1 WHERE id = ?",
                  (data["text"], data["id"]))
        conn.commit()
        conn.close()
        return {"status": "ok"}
    else:
        conn.close()
        return {"status": "unauthorized"}

@app.post("/delete-comment")
def delete_comment(data: Dict[str, Any]):
    """Delete comment"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT * FROM comments WHERE id = ?", (data["id"],))
    comment = c.fetchone()
    
    if not comment:
        conn.close()
        return {"status": "not_found"}
    
    if comment["user"] == data["user"] or is_admin(data["user"]):
        c.execute("DELETE FROM comments WHERE id = ?", (data["id"],))
        conn.commit()
        conn.close()
        return {"status": "ok"}
    else:
        conn.close()
        return {"status": "unauthorized"}
# =========================
# RATINGS
# =========================
@app.get("/get-ratings")
def get_ratings():
    """Get all ratings"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT productId, value, user FROM ratings")
    rows = c.fetchall()
    conn.close()
    
    ratings_dict = {}
    for row in rows:
        pid = str(row["productId"])
        if pid not in ratings_dict:
            ratings_dict[pid] = {"total": 0, "count": 0, "userRatings": {}}
        ratings_dict[pid]["total"] += row["value"]
        ratings_dict[pid]["count"] += 1
        ratings_dict[pid]["userRatings"][row["user"]] = row["value"]
    
    return JSONResponse(ratings_dict)

@app.post("/rate")
def rate(rating: RatingData):
    """Add or update rating"""
    conn = get_db()
    c = conn.cursor()
    
    # Check if user already rated this product
    c.execute("SELECT value FROM ratings WHERE productId = ? AND user = ?",
              (rating.productId, rating.user))
    existing = c.fetchone()
    
    if existing:
        c.execute("UPDATE ratings SET value = ? WHERE productId = ? AND user = ?",
                  (rating.value, rating.productId, rating.user))
    else:
        c.execute("INSERT INTO ratings (productId, user, value) VALUES (?, ?, ?)",
                  (rating.productId, rating.user, rating.value))
    
    conn.commit()
    conn.close()
    
    return {"status": "ok"}

@app.post("/delete-rating")
def delete_rating(data: Dict[str, Any]):
    """Delete rating"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("DELETE FROM ratings WHERE productId = ? AND user = ?",
              (data["productId"], data["user"]))
    
    conn.commit()
    conn.close()
    
    return {"status": "ok" if c.rowcount > 0 else "fail"}


# =========================
# VIEW TRACKING
# =========================
@app.post("/track-view")
def track_view(data: Dict[str, Any]):
    """Track product view"""
    product_id = data["productId"]
    user = data.get("user", "Guest") or "Guest"

    conn = get_db()
    c = conn.cursor()
    
    # Update views
    c.execute("SELECT view_count FROM views WHERE productId = ?", (product_id,))
    existing = c.fetchone()
    
    if existing:
        c.execute("UPDATE views SET view_count = view_count + 1 WHERE productId = ?",
                  (product_id,))
    else:
        c.execute("INSERT INTO views (productId, view_count) VALUES (?, ?)",
                  (product_id, 1))
    
    # Update favored
    c.execute("SELECT total, byUser FROM favored WHERE productId = ?", (product_id,))
    existing_favored = c.fetchone()
    
    if existing_favored:
        by_user = json.loads(existing_favored["byUser"])
        by_user[user] = by_user.get(user, 0) + 1
        by_user_json = json.dumps(by_user)
        c.execute("UPDATE favored SET total = total + 1, byUser = ? WHERE productId = ?",
                  (by_user_json, product_id))
    else:
        by_user = {user: 1}
        by_user_json = json.dumps(by_user)
        c.execute("INSERT INTO favored (productId, total, byUser) VALUES (?, ?, ?)",
                  (product_id, 1, by_user_json))
    
    conn.commit()
    conn.close()
    
    return {"status": "ok"}

@app.get("/get-views")
def get_views():
    """Get view counts for all products"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT productId, view_count FROM views")
    rows = c.fetchall()
    conn.close()
    
    views_dict = {str(row["productId"]): row["view_count"] for row in rows}
    return JSONResponse(views_dict)


# =========================
# RECOMMENDATIONS
# =========================
@app.get("/get-recommended/{product_id}")
def get_recommended(product_id: int):
    """Get 40 recommended products for a product page"""
    conn = get_db()
    c = conn.cursor()
    
    # Get all products
    c.execute("SELECT * FROM products")
    all_products = [dict(row) for row in c.fetchall()]
    
    # Get current product
    current_product = next((p for p in all_products if p["id"] == product_id), None)
    
    if not current_product:
        conn.close()
        return {"products": []}
    
    # Get ratings
    c.execute("SELECT productId, user, value FROM ratings")
    ratings_rows = c.fetchall()
    ratings = {}
    for row in ratings_rows:
        pid = str(row["productId"])
        if pid not in ratings:
            ratings[pid] = {"total": 0, "count": 0, "userRatings": {}}
        ratings[pid]["total"] += row["value"]
        ratings[pid]["count"] += 1
    
    # Get favored
    c.execute("SELECT productId, total FROM favored")
    favored = {str(row["productId"]): row["total"] for row in c.fetchall()}
    
    conn.close()
    
    def get_avg_rating(pid):
        pid_str = str(pid)
        if pid_str in ratings and ratings[pid_str]["count"] > 0:
            return ratings[pid_str]["total"] / ratings[pid_str]["count"]
        return 0
    
    def get_favored_count(pid):
        return favored.get(str(pid), 0)
    
    # 1. Related products (same category) - 10 products
    related = [p for p in all_products if p.get("category") == current_product.get("category") and p["id"] != product_id][:10]
    
    # 2. Highest rated products - 10 products
    highest_rated = sorted([p for p in all_products if p["id"] != product_id], 
                           key=lambda p: get_avg_rating(p["id"]), 
                           reverse=True)[:10]
    
    # 3. Most favored products - 10 products
    favored_products = sorted([p for p in all_products if p["id"] != product_id],
                              key=lambda p: get_favored_count(p["id"]),
                              reverse=True)[:10]
    
    # 4. Additional same category random products - 10 products
    same_category_random = [p for p in all_products if p.get("category") == current_product.get("category") and p["id"] != product_id and p not in related]
    random.shuffle(same_category_random)
    same_category_random = same_category_random[:10]
    
    # Combine all (max 40)
    recommended = []
    seen_ids = set()
    
    for p in related + favored_products + highest_rated + same_category_random:
        if p["id"] not in seen_ids and len(recommended) < 40:
            recommended.append(p)
            seen_ids.add(p["id"])
    
    return {"products": recommended}


# =========================
# MAIN ROUTES (SERVE HTML)
# =========================
@app.get("/")
def home():
    return FileResponse("templates/index.html")

@app.get("/shop")
def shop():
    return FileResponse("templates/shop.html")

@app.get("/product")
def product():
    return FileResponse("templates/product.html")

@app.get("/user")
def user():
    return FileResponse("templates/user.html")

# =========================
# RUN
# =========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)