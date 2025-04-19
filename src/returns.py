# Textual screen for processing product returns in a POS system.
# Features:
# - Load a receipt by ID
# - Add return items
# - Undo return items
# - Finalize transaction: issue refund, update inventory, log return
# - Lock the original receipt in sales.json to prevent multiple returns

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Input, Button, Static
from textual.events import Key
from textual.binding import Binding
from pathlib import Path
from datetime import datetime
import json

# File paths for inventory, sales, and return logs
DATA_PATH = Path(__file__).parent.parent / "data"
PRODUCTS_FILE = DATA_PATH / "products.json"
SALES_FILE = DATA_PATH / "sales.json"
RETURNS_FILE = DATA_PATH / "returns.json"

class ReturnsScreen(Screen):
    # Keyboard bindings for actions
    BINDINGS = [
        Binding("f3", "back", "Back to Menu"),
        Binding("f6", "show_summary", "Add Item + Show Summary"),
        Binding("f7", "undo_return_item", "Undo Last Item"),
        Binding("f8", "finalize_return", "Complete Transaction"),
    ]

    def compose(self) -> ComposeResult:
        """Create and organize all UI elements on the screen."""
        # Inputs and buttons
        self.receipt_id_input = Input(placeholder="Enter Receipt ID")
        self.load_button = Button("Load Receipt", id="load_receipt")
        self.receipt_area = Static("")

        self.item_id_input = Input(placeholder="Item ID/Name")
        self.quantity_input = Input(placeholder="Quantity")

        self.undo_info = Static("To undo an addition, type the item and quantity below")
        self.undo_item_id_input = Input(placeholder="Undo Item ID/Name")
        self.undo_quantity_input = Input(placeholder="Undo Quantity")

        self.return_summary_area = Static("Items being returned:")

        # Add widgets to screen
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

        # Track state
        self.returned_items = []
        self.sale = None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle 'Load Receipt' button press."""
        if event.button.id == "load_receipt":
            self.load_receipt()

    def load_receipt(self) -> None:
        """Load and display receipt details from sales.json by ID."""
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

        self.sale = next((s for s in sales if str(s["id"]) == receipt_id), None)
        if not self.sale:
            self.receipt_area.update(f"[red]Sale with ID {receipt_id} not found.[/red]")
            return

        # Safeguard: prevent returns on locked (already returned) receipts
        if self.sale.get("locked"):
            self.receipt_area.update(f"[red]Sale ID {receipt_id} has already been returned and is locked.[/red]")
            self.sale = None
            return

        # Show the loaded receipt
        receipt_text = "[b]Receipt Details:[/b]\n"
        for item in self.sale["items"]:
            receipt_text += f"- {item['name']} (SKU: {item['sku']}), Quantity: {item['quantity']}, Price: ${item['price']:.2f}\n"
        receipt_text += f"\n[b]Total:[/b] ${self.sale['total']:.2f}"
        self.receipt_area.update(receipt_text)

    def add_return_item(self) -> None:
        """Add an item to the return list, checking validity."""
        if not self.sale:
            self.return_summary_area.update("[red]Please load a receipt first.[/red]")
            return

        item_input = self.item_id_input.value.strip().lower()
        qty_input = self.quantity_input.value.strip()

        if not item_input or not qty_input.isdigit():
            self.return_summary_area.update("[red]Invalid item name/ID or quantity.[/red]")
            return

        quantity = int(qty_input)
        matched = None

        # Match input against items in the receipt
        for item in self.sale["items"]:
            if item_input == str(item["sku"]).lower() or item_input == item["name"].lower():
                matched = item
                break

        if not matched:
            self.return_summary_area.update("[red]Item not found in the loaded receipt.[/red]")
            return

        if quantity > matched["quantity"]:
            self.return_summary_area.update("[red]Return quantity exceeds purchased amount.[/red]")
            return

        # Add or update item in return list
        existing = next((i for i in self.returned_items if i["sku"] == matched["sku"]), None)
        if existing:
            existing["quantity"] += quantity
        else:
            self.returned_items.append({
                "sku": matched["sku"],
                "name": matched["name"],
                "quantity": quantity,
                "charge": matched["price"],
                "id": str(matched["sku"])  # for inventory update
            })

        # Clear inputs
        self.item_id_input.value = ""
        self.quantity_input.value = ""

    def action_show_summary(self) -> None:
        """Called by F6: Add return item and show summary."""
        if self.item_id_input.value.strip() and self.quantity_input.value.strip():
            self.add_return_item()
        self.update_return_summary()

    def update_return_summary(self) -> None:
        """Display the list of items selected for return and refund amounts."""
        if not self.returned_items:
            self.return_summary_area.update("Items being returned:\n[dim](None yet)[/dim]")
            return

        summary = "Items being returned:\n"
        for item in self.returned_items:
            charge = item["charge"] * item["quantity"]
            summary += f"- {item['name']} (SKU: {item['sku']}), Qty: {item['quantity']}, Refund: ${charge:.2f}\n"
        self.return_summary_area.update(summary)

    def action_undo_return_item(self) -> None:
        """Undo an item previously added to the return list (F7)."""
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

        # Clear inputs and refresh display
        self.undo_item_id_input.value = ""
        self.undo_quantity_input.value = ""
        self.update_return_summary()

    def action_finalize_return(self) -> None:
        """Finalize return transaction: update inventory, log return, lock sale."""
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
        self.lock_original_receipt()

    def update_inventory(self, item) -> None:
        """Update product stock in products.json by adding returned quantity."""
        try:
            with open(PRODUCTS_FILE, "r") as f:
                products = json.load(f)
        except Exception:
            return

        if item["id"] in products:
            products[item["id"]]["stock"] += item["quantity"]

        with open(PRODUCTS_FILE, "w") as f:
            json.dump(products, f, indent=2)

    def save_return_transaction(self, total_refund: float) -> None:
        """Append a return record to returns.json."""
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

    def lock_original_receipt(self) -> None:
        """Mark the original sale record in sales.json as locked after return."""
        try:
            with open(SALES_FILE, "r") as f:
                sales = json.load(f)
        except Exception:
            return

        for sale in sales:
            if sale["id"] == self.sale["id"]:
                sale["locked"] = True
                break

        with open(SALES_FILE, "w") as f:
            json.dump(sales, f, indent=2)

    def action_back(self) -> None:
        """Return to the previous screen."""
        self.app.pop_screen()
