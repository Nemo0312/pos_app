import json
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Container, Center
from textual.widgets import Static, Input, Button, DataTable
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.reactive import reactive
from textual.binding import Binding
from textual import events
from pathlib import Path
# import json
# from datetime import datetime
# import pyfiglet
# from inventory import * #inventory viewing logic is in inventory.py
from rich.text import Text
from textual import on
from main import load_inventory, save_sale

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
        
class SalesScreen(Screen):
    BINDINGS = [
        Binding("f3", "app.pop_screen", "Back"),
        Binding("f1", "help", "Help"),
        Binding("enter", "add_item", "Add Item"),
    ]

    cart = reactive([])

    def compose(self) -> ComposeResult:
        self.cart_table = DataTable(id="cart-table")
        self.cart_table.add_columns("SKU", "Name", "Qty", "Price")
        
        self.input_sku = Input(placeholder="Scan or enter SKU", id="sku-input")
        self.message = Static("", id="message")
        
        # Wrap the Vertical container in a list
        yield Vertical(
            Horizontal(
                Vertical(
                    Static("ADD ITEM", classes="header"),
                    self.input_sku,
                    self.message,
                    Button("Complete Sale", id="finish", variant="success"),
                    classes="input-panel"
                ),
                Vertical(
                    Static("CART", classes="header"),
                    self.cart_table,
                    classes="cart-panel"
                ),
            )
        )

    def on_mount(self) -> None:
        self.input_sku.focus()
        

    @on(Input.Submitted, "#sku-input")
    def add_item(self) -> None:
        input_text = self.input_sku.value.strip()
        if not input_text:
            self.message.update("Please enter a SKU")
            return
        
        # Split input into SKU and quantity (default quantity is 1)
        if '.' in input_text:
            try:
                sku, quantity_str = input_text.split('.')
                quantity = int(quantity_str)
                if quantity <= 0:
                    self.message.update("Quantity must be positive")
                    return
            except ValueError:
                self.message.update("Invalid quantity format (use SKU.QUANTITY)")
                return
        else:
            sku = input_text
            quantity = 1
            
        inventory = load_inventory()
        if sku not in inventory:
            self.message.update(f"SKU {sku} not found")
            return
            
        item = inventory[sku]
        
        # Check if item already exists in cart
        existing_index = next((i for i, x in enumerate(self.cart) if x["sku"] == sku), None)
        
        if existing_index is not None:
            # Update existing item
            self.cart[existing_index]["quantity"] += quantity
            self.cart[existing_index]["total"] += item["price"] * quantity
        else:
            # Add new item
            self.cart.append({
                "sku": sku,
                "name": item["name"],
                "quantity": quantity,
                "price": item["price"],
                "total": item["price"] * quantity
            })
        
        # This will trigger watch_cart() automatically
        # self.cart = self.cart.copy()  # Force reactive update
        self.watch_cart()
        
        self.input_sku.value = ""
        self.message.update(f"Added {item['name']}")
        self.input_sku.focus()

    def watch_cart(self) -> None:
        """Automatically called when cart changes"""
        self.cart_table.clear()
        
        
       # Create a dictionary to combine duplicate SKUs
        combined_items = {}
        for item in self.cart:
            if item["sku"] in combined_items:
                combined_items[item["sku"]]["quantity"] += item["quantity"]
                combined_items[item["sku"]]["total"] += item["total"]
            else:
                combined_items[item["sku"]] = item.copy()
        
        # Display the combined items
        for sku, item in combined_items.items():
            self.cart_table.add_row(
                sku,
                item["name"],
                str(item["quantity"]),
                f"${item['total']:.2f}"
            )
        
        # Add total row if cart has items
        if combined_items:
            total = sum(item["total"] for item in combined_items.values())
            self.cart_table.add_row(
                "", 
                "", 
                Text("Total:", style="bold"), 
                Text(f"${total:.2f}", style="bold green")
            )

    @on(Button.Pressed, "#finish")
    def complete_sale(self) -> None:
        if not self.cart:
            self.message.update("Cart is empty")
            return
            
        total = sum(item["price"] for item in self.cart)
        save_sale(self.cart, total)
        self.message.update(f"Sale completed! Total: ${total:.2f}")
        self.cart = []  # Clear cart (triggers watch_cart)
        self.input_sku.focus()