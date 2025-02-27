import json
from datetime import datetime

def add_item_to_sale(item_id: str, quantity: int):
    """Add an item to a sale, checking stock availability."""
    with open("data/products.json", "r") as f:
        products = json.load(f)
    
    if item_id in products:
        item = products[item_id]
        if item["stock"] >= quantity:
            return {"name": item["name"], "total": item["price"] * quantity}
        else:
            return {"error": "Not enough stock!"}
    return {"error": "Item not found!"}

def save_sale(cart: list, total: float):
    """Save the sale details to sales.json."""
    with open("data/sales.json", "r") as f:
        sales = json.load(f)
    
    sale = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": cart,
        "total": total
    }
    sales.append(sale)
    
    with open("data/sales.json", "w") as f:
        json.dump(sales, f, indent=2)