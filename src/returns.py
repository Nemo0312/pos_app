from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Input, Button, Static
from textual.events import Key
from textual.binding import Binding
from pathlib import Path
from datetime import datetime
import json

# Paths to files
DATA_PATH = Path(__file__).parent.parent / "data"
PRODUCTS_FILE = DATA_PATH / "products.json"
SALES_FILE = DATA_PATH / "sales.json"
RETURNS_FILE = DATA_PATH / "returns.json"

class ReturnsScreen(Screen):
    # Key bindings for common actions
    BINDINGS = [
        Binding("f3", "back", "Back to Menu"),
        Binding("f6", "show_summary", "Add Item + Show Summary"),
        Binding("f7", "undo_return_item", "Undo Last Item"),
        Binding("f8", "finalize_return", "Complete Transaction"),
    ]
    # UI layout
    def compose(self) -> ComposeResult:
        # Create and store widgets for later access
        self.receipt_id_input = Input(placeholder="Enter Receipt ID")
        self.load_button = Button("Load Receipt", id="load_receipt")

        self.receipt_area = Static("")
        self.item_id_input = Input(placeholder="Item ID/Name")
        self.quantity_input = Input(placeholder="Quantity")

        self.undo_info = Static("To undo an addition, type the item and quantity below")
        self.undo_item_id_input = Input(placeholder="Undo Item ID/Name")
        self.undo_quantity_input = Input(placeholder="Undo Quantity")

        self.return_summary_area = Static("Items being returned:")

        # Display the input layout
        yield Label("Receipt ID:")
        yield self.receipt_id_input
        yield self.load_button
        yield self.receipt_area
        yield Label("Item ID/Name:")
        yield self.item_id_input
        yield Label("Quantity:")
        yield self.quantity_input
        yield self.undo_info
        yield self.undo_item_id_input
        yield self.undo_quantity_input
        yield self.return_summary_area
        yield Static("Press F6 to add item and show summary.\nPress F7 to undo an item.\nPress F8 to complete transaction.\nPress F3 to return to the main screen.")

        self.returned_items = []
        self.sale = None
    # Handle button presses
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "load_receipt":
            self.load_receipt()
    # Load a receipt by ID from sales.json
    def load_receipt(self) -> None:
        receipt_id = self.receipt_id_input.value.strip()
        if not receipt_id:
            self.receipt_area.update("[red]Receipt ID cannot be empty.[/red]")
            return

        try:
            with open(SALES_FILE) as f:
                sales = json.load(f)
        except Exception as e:
            self.receipt_area.update(f"[red]Error loading sales: {e}[/red]")
            return
            
        # Search for a matching sale by ID
        self.sale = next((s for s in sales if str(s["id"]) == receipt_id), None)
        if not self.sale:
            self.receipt_area.update(f"[red]Sale with ID {receipt_id} not found.[/red]")
            return
            
        # Display receipt details
        receipt_text = "[b]Receipt Details:[/b]\n"
        for item in self.sale["items"]:
            receipt_text += f"- {item['name']} (SKU: {item['sku']}), Quantity: {item['quantity']}, Price: ${item['price']:.2f}\n"
        receipt_text += f"\n[b]Total:[/b] ${self.sale['total']:.2f}"
        self.receipt_area.update(receipt_text)
    
    # Add an item to the return list
    def add_return_item(self) -> None:
        if not self.sale:
            self.return_summary_area.update("[red]Please load a receipt first.[/red]")
            return

        item_input = self.item_id_input.value.strip().lower()
        qty_input = self.quantity_input.value.strip()

        if not item_input or not qty_input.isdigit():
            self.return_summary_area.update("[red]Invalid item name/ID or quantity.[/red]")
            return

        quantity = int(qty_input)
        matched = None # Match input against receipt items
        for item in self.sale["items"]:
            if item_input == str(item["sku"]).lower() or item_input == item["name"].lower():
                matched = item
                break

        if not matched:
            self.return_summary_area.update("[red]Item not found in the loaded receipt.[/red]")
            return

        # Prevent returning more than it was bought
        if quantity > matched["quantity"]:
            self.return_summary_area.update("[red]Return quantity exceeds purchased amount.[/red]")
            return

        # Add or update the item in the return list
        existing = next((i for i in self.returned_items if i["sku"] == matched["sku"]), None)
        if existing:
            existing["quantity"] += quantity
        else:
            self.returned_items.append({
                "sku": matched["sku"],
                "name": matched["name"],
                "quantity": quantity,
                "charge": matched["price"],
                "id": str(matched["sku"])  # matches products.json key
            })

        self.item_id_input.value = ""
        self.quantity_input.value = ""

    # F6: Show return summary (and add item first if fields are filled)
    def action_show_summary(self) -> None:
        
        if self.item_id_input.value.strip() and self.quantity_input.value.strip():
            self.add_return_item()

        self.update_return_summary()

    # Display current list of returned items
    def update_return_summary(self) -> None:
        if not self.returned_items:
            self.return_summary_area.update("Items being returned:\n[dim](None yet)[/dim]")
            return

        summary = "Items being returned:\n"
        for item in self.returned_items:
            charge = item["charge"] * item["quantity"]
            summary += f"- {item['name']} (SKU: {item['sku']}), Qty: {item['quantity']}, Refund: ${charge:.2f}\n"
        self.return_summary_area.update(summary)

    # F7: Undo the added return item (or reduce quantity)
    def action_undo_return_item(self) -> None:
        item_input = self.undo_item_id_input.value.strip().lower()
        qty_input = self.undo_quantity_input.value.strip()

        if not item_input or not qty_input.isdigit():
            self.return_summary_area.update("[red]Invalid undo entry.[/red]")
            return

        quantity = int(qty_input)
        for item in self.returned_items:
            if item_input == str(item["sku"]).lower() or item_input == item["name"].lower():
                item["quantity"] -= quantity
                if item["quantity"] <= 0:
                    self.returned_items.remove(item)
                break

        self.undo_item_id_input.value = ""
        self.undo_quantity_input.value = ""
        self.update_return_summary()

    # F8: Finalize the return and log transaction
    def action_finalize_return(self) -> None:
        if not self.returned_items:
            self.return_summary_area.update("[red]No items to return.[/red]")
            return

        total_refund = 0
        summary = "[bold green]Transaction completed:[/bold green]\n"
        for item in self.returned_items:
            charge = item["charge"] * item["quantity"]
            total_refund += charge
            summary += f"- {item['name']} (SKU: {item['sku']}) x {item['quantity']} → Refund: ${charge:.2f}\n"
            self.update_inventory(item)

        summary += f"\n[bold]Total Refunded:[/bold] ${total_refund:.2f}"
        self.return_summary_area.update(summary)
        self.save_return_transaction(total_refund)

    # Update stock levels in products.json
    def update_inventory(self, item) -> None:
        try:
            with open(PRODUCTS_FILE, "r") as f:
                products = json.load(f)
        except Exception:
            return

        if item["id"] in products:
            products[item["id"]]["stock"] += item["quantity"]

        with open(PRODUCTS_FILE, "w") as f:
            json.dump(products, f, indent=2)

    # Record the return in returns.json
    def save_return_transaction(self, total_refund: float) -> None:
        return_data = {
            "id": int(datetime.now().timestamp()),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": self.returned_items,
            "total_refund": round(total_refund, 2)
        }

        if RETURNS_FILE.exists():
            with open(RETURNS_FILE, "r") as f:
                returns = json.load(f)
        else:
            returns = []

        returns.append(return_data)

        with open(RETURNS_FILE, "w") as f:
            json.dump(returns, f, indent=2)

    # F3: Return to the main screen
    def action_back(self) -> None:
        self.app.pop_screen()
