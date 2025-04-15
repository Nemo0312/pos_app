# returns.py
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Input, Button, Static
from textual.binding import Binding
from pathlib import Path
import json
import datetime

DATA_PATH = Path(__file__).parent.parent / "data"
PRODUCTS_FILE = DATA_PATH / "products.json"
SALES_FILE = DATA_PATH / "sales.json"
RETURNS_FILE = DATA_PATH / "returns.json"

class ReturnsScreen(Screen):
    BINDINGS = [
        Binding("f7", "show_return_summary", "Show Return Summary"),
        Binding("f8", "complete_transaction", "Complete Transaction"),
        Binding("f3", "back", "Back to Menu"),
    ]

    def compose(self) -> ComposeResult:
        self.receipt_id_input = Input(placeholder="Enter Receipt ID", id="receipt_input")
        self.receipt_button = Button("Load Receipt", id="load_receipt_btn")

        self.item_id_input = Input(placeholder="Enter Item ID/Name", id="item_input")
        self.quantity_input = Input(placeholder="Enter Quantity", id="qty_input")

        # Undo input fields
        self.undo_item_id_input = Input(placeholder="Undo Item ID/Name", id="undo_item_input")
        self.undo_quantity_input = Input(placeholder="Undo Quantity", id="undo_qty_input")

        yield Static("Receipt ID:")
        yield self.receipt_id_input
        yield self.receipt_button

        self.receipt_details_area = Static("")
        yield self.receipt_details_area

        yield Static("Item ID/Name:")
        yield self.item_id_input

        yield Static("Quantity:")
        yield self.quantity_input

        yield Button("F7: Show Return Summary", id="show_summary")
        yield Button("F8: Complete Transaction", id="complete_transaction")

        # Undo section
        yield Static("To undo an addition, type the item and quantity below:")
        yield Static("Undo Item ID/Name:")
        yield self.undo_item_id_input
        yield Static("Undo Quantity:")
        yield self.undo_quantity_input

        self.returned_items = []  # List to store items being returned
        self.return_summary_area = Static("")
        yield self.return_summary_area

        self.message_area = Static("")
        yield self.message_area

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "load_receipt_btn":
            await self.load_receipt()

    async def load_receipt(self):
        receipt_id = self.receipt_id_input.value.strip()
        if not receipt_id:
            return self.display_message("Receipt ID cannot be empty.", error=True)

        try:
            with open(SALES_FILE) as f:
                sales = json.load(f)
        except Exception:
            return self.display_message("Failed to load sales data.", error=True)

        sale = next((s for s in sales if str(s['id']) == receipt_id), None)
        if not sale:
            return self.display_message(f"Sale with ID {receipt_id} not found.", error=True)

        self.sale = sale
        self.display_receipt(sale)

    def display_receipt(self, sale):
        receipt_info = f"[bold]Receipt ID:[/bold] {sale['id']}\n"
        receipt_info += f"[bold]Date:[/bold] {sale['date']}\n\n"

        receipt_info += "[bold]Items:[/bold]\n"
        for item in sale['items']:
            receipt_info += f"- SKU: {item['sku']} - {item['name']} (x{item['quantity']}) - ${item['price'] * item['quantity']:.2f}\n"

        receipt_info += f"\n[bold]Total:[/bold] ${sale['total']:.2f}"

        self.receipt_details_area.update(receipt_info)

    def display_message(self, message, error=False):
        self.message_area.update(f"[{'bold red' if error else 'green'}]{message}[/{'bold red' if error else 'green'}]")

    def action_show_return_summary(self):
        # Build return summary based on returned items
        return_summary = "Items being returned:\n"
        total_refund = 0
        for item in self.returned_items:
            charge = item['charge'] * item['quantity']
            return_summary += f"- {item['name']} (SKU: {item['sku']}) x {item['quantity']} → Charge: ${charge:.2f}\n"
            total_refund += charge

        return_summary += f"\n[bold]Total Refund:[/bold] ${total_refund:.2f}"
        self.return_summary_area.update(return_summary)

    async def on_input_changed(self, event: Input.Changed) -> None:
        # Check if we need to update the return summary when item ID and quantity are entered
        if event.input.id == "item_input" or event.input.id == "qty_input":
            item_id = self.item_id_input.value.strip()
            quantity = self.quantity_input.value.strip()

            if item_id and quantity.isdigit():
                quantity = int(quantity)

                # Find the item in the sale receipt
                item = next((i for i in self.sale['items'] if str(i['sku']) == item_id or i['name'].lower() == item_id.lower()), None)
                if item:
                    # Add to returned items
                    charge = item['price']
                    self.returned_items.append({
                        'sku': item['sku'],
                        'name': item['name'],
                        'quantity': quantity,
                        'charge': charge
                    })

                    # Show the return summary again
                    self.action_show_return_summary()
                else:
                    self.display_message("Item not found in the receipt.", error=True)
            else:
                self.display_message("Please enter a valid item and quantity.", error=True)

        elif event.input.id == "undo_item_input" or event.input.id == "undo_qty_input":
            # Check for undo request
            undo_item_id = self.undo_item_id_input.value.strip()
            undo_qty = self.undo_quantity_input.value.strip()

            if undo_item_id and undo_qty.isdigit():
                undo_qty = int(undo_qty)

                # Try to find the item to undo
                item_to_remove = next((item for item in self.returned_items if item['name'].lower() == undo_item_id.lower() or str(item['sku']) == undo_item_id), None)
                if item_to_remove:
                    # Remove the item from the returned items list
                    self.returned_items.remove(item_to_remove)

                    # Show the updated return summary
                    self.action_show_return_summary()
                    self.display_message(f"Undone return of {undo_item_id} (x{undo_qty}).", error=False)
                else:
                    self.display_message("Item not found in the return list.", error=True)
            else:
                self.display_message("Please enter a valid item and quantity to undo.", error=True)

    def action_complete_transaction(self):
        # Complete the return transaction and update inventory
        total_refund = 0
        return_details = "Items officially returned:\n"
        for item in self.returned_items:
            charge = item['charge'] * item['quantity']
            return_details += f"- {item['name']} (SKU: {item['sku']}) x {item['quantity']} → Refund: ${charge:.2f}\n"
            total_refund += charge

        return_details += f"\n[bold]Total Refund:[/bold] ${total_refund:.2f}"
        self.display_message(return_details)

        # Generate a new receipt for the return and save it in returns.json
        return_receipt = {
            "id": str(int(datetime.datetime.now().timestamp())),  # Generate a unique return receipt ID based on the timestamp
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": self.returned_items,
            "total": total_refund
        }

        try:
            # Save to returns.json
            try:
                with open(RETURNS_FILE, 'r') as f:
                    returns_data = json.load(f)
            except FileNotFoundError:
                returns_data = []

            returns_data.append(return_receipt)
            with open(RETURNS_FILE, 'w') as f:
                json.dump(returns_data, f, indent=2)

            # Update inventory based on returned items
            with open(PRODUCTS_FILE) as f:
                products = json.load(f)

            for item in self.returned_items:
                product = next((p for p in products if p['sku'] == item['sku']), None)
                if product:
                    product['stock'] += item['quantity']

            with open(PRODUCTS_FILE, "w") as f:
                json.dump(products, f, indent=2)

            # Complete transaction and go back to the main screen
            self.display_message(f"[green]Transaction completed. Total Refund: ${total_refund:.2f}[/green]")
            self.app.pop_screen()  # Go back to the main screen after completing the transaction

        except Exception as e:
            self.display_message(f"Error completing transaction: {e}", error=True)
