import json
from src.inventory import get_inventory

def test_get_inventory():
    with open("data/products.json", "r") as f:
        expected = json.load(f)
    assert get_inventory() == expected