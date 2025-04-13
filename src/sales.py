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
        Binding("ctrl+z", "undo_last", "Undo Last"),
        Binding("-", "undo_last", "Undo Last"),
    ]

    cart = reactive([])
    action_history = []  # Track all actions for undo
    selected_item = reactive(None)  # Track selected item for editing

    def compose(self) -> ComposeResult:
        self.cart_table = DataTable(id="cart-table")
        self.cart_table.cursor_type = "row"  # Ensure row selection is enabled
        self.cart_table.add_columns("SKU", "Name", "Qty", "Price")
        
        self.input_sku = Input(placeholder="Scan or enter SKU", id="sku-input")
        self.input_qty = Input(placeholder="Enter new quantity", id="qty-input")
        self.message = Static("", id="message")
        
                # Add operations help box
        operations_help = Static(
            """[b]Operations Help[/b]
─────────────────────────────
 [b]Add Item[/b]: SKU.QUANTITY       
 [b]Edit Qty[/b]: Select + New Value 
 [b]Delete[/b]: Select + "-" or "d"  
 [b]Undo[/b]: Ctrl+Z/-               
 [b]Complete Sale[/b]: Finish Button 
─────────────────────────────""",
            classes="operations-help"
        )
        
        yield Vertical(
            Horizontal(
                Vertical(
                    Static("ADD ITEM", classes="header"),
                    self.input_sku,
                    self.input_qty,
                    self.message,
                    Horizontal(
                        Button("Update Qty", id="update", variant="primary", disabled=True),
                        Button("Delete Item", id="delete", variant="error", disabled=True),
                        Button("Undo Last", id="undo", variant="warning"),
                        Button("Complete Sale", id="finish", variant="success"),
                        classes="button-group"
                    ),
                    classes="input-panel"
                ),
                Vertical(
                    Static("CART", classes="header"),
                    self.cart_table,
                    operations_help,
                    classes="cart-panel"
                ),
            )
        )

    def on_mount(self) -> None:
        self.input_sku.focus()
        # self.cart_table.focus()  # Ensure the table can receive focus
        
    def add_to_history(self, action_type: str, data: dict):
        """Record an action in history"""
        self.action_history.append({
            "type": action_type,
            "data": data,
            "snapshot": [item.copy() for item in self.cart]  # Save cart state
        })

    def watch_selected_item(self, selected_item: dict | None) -> None:
 
        # Remove disabling of the quantity input field so it is always enabled.
        # self.input_qty.disabled = selected_item is None

        self.query_one("#update").disabled = selected_item is None
        self.query_one("#delete").disabled = selected_item is None

        if selected_item:
            # Pre-fill the quantity field with the selected item's current quantity for editing.
            self.input_qty.value = str(selected_item["quantity"])
            self.input_qty.focus()
        else:
            # Clear the quantity field for new item entries and focus back on SKU input.
            self.input_qty.value = ""
            self.input_sku.focus()

    @on(DataTable.RowSelected, "#cart-table")
    def handle_row_selected(self, event: DataTable.RowSelected) -> None:
        """When a row is selected in the cart table"""
        # Get the row key (we'll use the SKU as the key when adding rows)
        row_key = event.row_key.value if event.row_key else None
        
        if row_key and row_key != "total":  # Skip the total row
            # Find the item in cart with matching SKU
            self.selected_item = next((item for item in self.cart if item["sku"] == row_key), None)
        else:
            self.selected_item = None
            
    @on(Button.Pressed, "#delete")
    def delete_selected_item(self) -> None:
        """Delete the currently selected item"""
        if not self.selected_item:
            return
        
        sku = self.selected_item["sku"]
        item_name = self.selected_item["name"]
        
        # Record deletion in history
        self.add_to_history("delete_item", {
            "sku": sku,
            "item": self.selected_item.copy()
        })
        # Remove item from cart
        self.cart = [item for item in self.cart if item["sku"] != sku]
        self.cart = self.cart.copy()  # Force UI update
        self.message.update(f"Removed {item_name} from cart")
        self.input_sku.focus()
        self.selected_item = None
        
    def action_undo_last(self) -> None:
        """Action triggered by ctrl+z"""
        self.undo_last_entry()
            
        
    
    @on(Button.Pressed, "#undo")
    def undo_last_entry(self) -> None:
        """Undo the last added item"""
        if not self.action_history:
            self.message.update("Nothing to undo")
            return
            
        last_action = self.action_history.pop()
        
        if last_action["type"] == "add_item":
            # Undo add item - restore previous cart state
            self.cart = [item.copy() for item in last_action["snapshot"]]
            self.message.update(f"Undo: Removed {last_action['data']['quantity']} of {last_action['data']['sku']}")
            
        elif last_action["type"] == "edit_qty":
            # Restore previous quantity
            sku = last_action["data"]["sku"]
            old_qty = last_action["data"]["old_qty"]
            
            new_cart = []
            for item in self.cart:
                if item["sku"] == sku:
                    new_item = item.copy()
                    new_item["quantity"] = old_qty
                    new_item["total"] = old_qty * item["price"]
                    new_cart.append(new_item)
                else:
                    new_cart.append(item.copy())
            self.cart = new_cart
            self.message.update(f"Undo: Restored quantity to {old_qty}")
            
        elif last_action["type"] == "delete_item":
            restored_item = last_action["data"]["item"]
            
            # Check if item already exists in cart
            existing_index = next((i for i, x in enumerate(self.cart) if x["sku"] == restored_item["sku"]), None)
            
            if existing_index is not None:
                # If item exists, add the restored quantity to it
                self.cart[existing_index]["quantity"] += restored_item["quantity"]
                self.cart[existing_index]["total"] += restored_item["total"]
            else:
                # Otherwise add the item back as it was
                self.cart.append(restored_item.copy())
            
            self.message.update(f"Undo: Restored {restored_item['name']} (qty: {restored_item['quantity']})")
            
        # Force UI update
        self.watch_cart()
        # self.message.update("Last item removed")
        self.input_sku.focus()

    @on(Button.Pressed, "#update")
    @on(Input.Submitted, "#qty-input")
    def update_quantity(self) -> None:
        """Update the quantity of the selected item"""
        if not self.selected_item:
            return
        """Update quantity or delete item if input is '-' or 'd'"""       
        input_text = self.input_qty.value.strip().lower()
        
        # Handle deletion if input is '-' or 'd'
        if input_text in ('-', 'd'):
            sku = self.selected_item["sku"]
            item_name = self.selected_item["name"]
            
            # Record deletion in history
            self.add_to_history("delete_item", {
                "sku": sku,
                "item": self.selected_item.copy()
            })
            
            # Remove item from cart
            self.cart = [item for item in self.cart if item["sku"] != sku]
            self.message.update(f"Removed {item_name} from cart")
            self.input_qty.value = ""
            self.input_qty.placeholder = "Enter new quantity"
            self.input_sku.focus()
            self.selected_item = None
            return

        
        try:
            new_qty = int(self.input_qty.value)
            if new_qty <= 0:
                self.message.update("Quantity must be positive")
                return

            inventory = load_inventory()
            sku = self.selected_item["sku"]
            item_name = self.selected_item["name"]  # Store name before clearing
            
            # Check stock availability
            if inventory[sku]["stock"] < new_qty:
                self.message.update(f"Only {inventory[sku]['stock']} available in stock")
                return
            
            # Record state before modification
            self.add_to_history("edit_qty", {
                "sku": sku,
                "old_qty": self.selected_item["quantity"],
                "new_qty": new_qty
            })

            # Update quantity in a new cart
            new_cart = []
            for item in self.cart:
                if item["sku"] == sku:
                    new_item = item.copy()
                    new_item["quantity"] = new_qty
                    new_item["total"] = new_item["price"] * new_qty
                    new_cart.append(new_item)
                else:
                    new_cart.append(item.copy())
            
            # Force cart update
            self.cart = new_cart
            self.message.update(f"Updated {item_name} quantity")
            self.input_qty.value = ""
            self.input_qty.placeholder = "Enter new quantity"
            self.input_sku.focus()
            self.selected_item = None  # Clear selection after update
        except ValueError:
            self.message.update("Please enter a valid number")

    @on(Input.Submitted, "#sku-input")
    @on(Input.Submitted, "#qty_input")
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
        
        # Record action before modifying cart
        self.add_to_history("add_item", {
            "sku": sku,
            "quantity": quantity,
            "existing_index": existing_index,
            "current_qty": self.cart[existing_index]["quantity"] if existing_index is not None else 0
        })
        
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
        
        self.watch_cart()
        self.input_sku.value = ""
        self.message.update(f"Added {item['name']}")
        self.input_sku.focus()# Re-focus SKU input after adding item


    def watch_cart(self) -> None:
        """Automatically called when cart changes"""
        self.cart_table.clear()
        self.selected_item = None  # Clear selection when cart changes
        
        # Create a dictionary to combine duplicate SKUs
        combined_items = {}
        for item in self.cart:
            if item["sku"] in combined_items:
                combined_items[item["sku"]]["quantity"] += item["quantity"]
                combined_items[item["sku"]]["total"] += item["total"]
            else:
                combined_items[item["sku"]] = item.copy()
        
        # Display the combined items with row keys
        for sku, item in combined_items.items():
            self.cart_table.add_row(
                sku,
                item["name"],
                str(item["quantity"]),
                f"${item['total']:.2f}",
                key=sku  # Important: Set the row key to SKU
            )
        
        # Add total row if cart has items
        if combined_items:
            total = sum(item["total"] for item in combined_items.values())
            self.cart_table.add_row(
                "", 
                "", 
                Text("Total:", style="bold"), 
                Text(f"${total:.2f}", style="bold green"),
                key="total"  # Different key for total row
            )

    @on(Button.Pressed, "#finish")
    def complete_sale(self) -> None:
        if not self.cart:
            self.message.update("Cart is empty")
            return
            
        total = sum(item["total"] for item in self.cart)
        save_sale(self.cart, total)
        self.message.update(f"Sale completed! Total: ${total:.2f}")
        self.cart = []  # Clear cart (triggers watch_cart)
        self.action_history = []  # Clear history after sale
        self.input_sku.focus()
        
    # Add this CSS to your app
    CSS = """
    .operations-help {
        dock: bottom;
        width: 40;
        margin: 1 0 0 0;
        padding: 1;
        background: $panel;
        border: round $primary;
        color: $text;
    }

    .operations-help Static {
        width: 100%;
    }
    """