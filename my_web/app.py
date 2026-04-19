
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# 🔥 PRODUSE (poți pune 100+)
PRODUCTS = [
    {"id": i, "name": f"Produs {i}", "price": i * 5}
    for i in range(1, 101)
]

PER_PAGE = 5

import json

@app.route("/products-json")
def products_json():
    with open("products.json", "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/shop")
def shop():
    return render_template("shop.html")

# 🔥 API pentru shop.js
@app.route("/products")
def get_products():
    page = int(request.args.get("page", 1))

    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE

    items = PRODUCTS[start:end]

    return jsonify({
        "page": page,
        "items": items,
        "total": len(PRODUCTS)
    })

if __name__ == "__main__":
    app.run(debug=True)