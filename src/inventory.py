import json

def get_inventory():
    """Retrieve the current inventory from products.json."""
    with open("data/products.json", "r") as f:
        return json.load(f)