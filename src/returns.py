import json
from datetime import datetime

def process_return_update(receipt_id, returned_items):
    # --- Restock items in products.json ---
    with open("data/products.json", "r") as f:
        products = json.load(f)

    for item in returned_items:
        if item["item_id"] in products:
            products[item["item_id"]]["stock"] += item["quantity"]

    with open("data/products.json", "w") as f:
        json.dump(products, f, indent=2)

    # --- Log return receipt in returns.json ---
    return_receipt = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "original_receipt_id": receipt_id,
        "returned_items": returned_items,
        "refund_total": sum(
            round((item["total"] / item["quantity"]) * item["quantity"], 2)
            for item in returned_items
        )
    }

    try:
        with open("data/returns.json", "r") as f:
            returns = json.load(f)
    except FileNotFoundError:
        returns = []

    returns.append(return_receipt)

    with open("data/returns.json", "w") as f:
        json.dump(returns, f, indent=2)
