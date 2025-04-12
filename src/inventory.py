# inventory.py
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Static, Input, Button
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.binding import Binding
from textual import events
from pathlib import Path
import json


DATA_PATH = Path(__file__).parent.parent / "data"
PRODUCTS_FILE = DATA_PATH / "products.json"

def get_inventory():
    """Retrieve the current inventory from products.json."""
    with open(PRODUCTS_FILE, "r") as f:
        return json.load(f)

        
class InventoryScreen(Screen):
    BINDINGS = [
        Binding("f3", "app.pop_screen", "Back"),
        Binding("f1", "help", "Help"),
        Binding("p", "page_mode", "Page Mode"),
        Binding("left", "prev_page", "Previous Page"),
        Binding("right", "next_page", "Next Page"),
        Binding("+", "next_page", "Next Page"),
        Binding("minus", "prev_page", "Previous Page"),  # Changed from "-" to "minus"
        Binding("2", "full_view", "Toggle Full/Paginated View")  # Updated description
    ]

    page = reactive(1)
    page_size = 10
    is_full_view = reactive(False)  # New reactive variable to track full view state

    CSS = """
    DataTable {
        height: 1fr;
        width: 1fr;
        border: round yellow;
    }
    Static.title {
        text-align: center;
        color: orange;
        margin-bottom: 1;
    }
    .status {
        margin-top: 1;
        text-align: center;
    }
    #controls {
        margin-top: 1;
    }
    Input {
        border: round #e8c28c;
        padding: 0 1;
    }
    Button {
        background: #3d2f1e;
        color: lightgoldenrodyellow;
        border: heavy #6e4e2e;
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        self.table = DataTable()
        self.table.add_columns("ID", "Category", "Name", "Price", "Stock", "Next Shipment", "Incoming Stock")
        self.table.zebra_stripes = True
        self.status = Static("", classes="status")
        self.search_input = Input(placeholder="Search by ID, name, or category (Enter to search)", id="search")
        self.update_table()

        yield Vertical(
            Static("[bold green]Inventory View[/bold green]", classes="title"),
            self.table,
            self.status,
            Horizontal(
                self.search_input,
                Button("Previous", id="prev"),
                Button("Next", id="next"),
                Button("Full View (2)", id="full"),
                id="controls"
            )
        )

    def update_table(self, inventory=None, filtered=False):
        """Update the table with inventory data, either paginated or filtered."""
        inventory = inventory or get_inventory()
        self.table.clear()
        if filtered or self.is_full_view:
            for i, ii in inventory.items():
                self.table.add_row(
                    i, ii["category"], ii["name"], f"${ii['price']:.2f}",
                    str(ii["stock"]), ii.get("next_ship", "N/A"), str(ii.get("next_ship_qty", 0))
                )
            self.status.update(f"[yellow]Showing {len(inventory)} items (Full View)[/yellow]")
        else:
            items = list(inventory.items())
            item_count = len(items)
            page_count = (item_count + self.page_size - 1) // self.page_size
            start_index = (self.page - 1) * self.page_size
            end_index = min(start_index + self.page_size, item_count)
            if start_index < item_count and self.page > 0:
                for item_id, item in items[start_index:end_index]:
                    self.table.add_row(
                        item_id, item["category"], item["name"], f"${item['price']:.2f}",
                        str(item["stock"]), item.get("next_ship", "N/A"), str(item.get("next_ship_qty", 0))
                    )
                self.status.update(f"[yellow]Showing items {start_index + 1}-{end_index} of {item_count} (Page {self.page}/{page_count})[/yellow]")
            else:
                self.status.update(f"[red]Page {self.page} out of range 1-{page_count}[/red]")

    def on_button_pressed(self, event: Button.Pressed):
        """Handle button presses for navigation."""
        inventory = get_inventory()
        item_count = len(inventory)
        page_count = (item_count + self.page_size - 1) // self.page_size
        if event.button.id == "prev" and self.page > 1 and not self.is_full_view:
            self.page -= 1
            self.update_table()
        elif event.button.id == "next" and self.page < page_count and not self.is_full_view:
            self.page += 1
            self.update_table()
        elif event.button.id == "full":
            self.is_full_view = not self.is_full_view
            self.update_table()

    def on_input_submitted(self, event: Input.Submitted):
        """Handle search and page number input."""
        if event.input.id == "search":
            search_term = event.value.strip().lower()
            
            if search_term == "p":
                self.action_page_mode()
                return
        
            inventory = get_inventory()
            if not search_term:
                self.update_table()
            elif search_term == "2":
                self.is_full_view = not self.is_full_view
                self.update_table()
            elif "page number" in self.search_input.placeholder:
                try:
                    new_page = int(search_term)
                    page_count = (len(inventory) + self.page_size - 1) // self.page_size
                    if 1 <= new_page <= page_count:
                        self.page = new_page
                        self.is_full_view = False  # Reset to paginated view
                        self.update_table()
                    else:
                        self.status.update(f"[red]Page must be 1-{page_count}[/red]")
                except ValueError:
                    self.status.update("[red]Invalid page number![/red]")
                self.search_input.placeholder = "Search by ID, name, or category (Enter to search)"
            else:
                try:
                    sku = int(search_term)
                    filtered = {k: v for k, v in inventory.items() if int(k) == sku}
                except ValueError:
                    filtered = {
                        k: v for k, v in inventory.items()
                        if search_term in v["name"].lower() or search_term in v["category"].lower()
                    }
                if filtered:
                    self.update_table(filtered, filtered=True)
                else:
                    self.status.update("[red]No items found![/red]")
            
            self.search_input.value = ""
            self.search_input.focus()

    def action_page_mode(self):
        """Enter page selection mode."""
        self.search_input.value = ""
        self.search_input.placeholder = "Enter page number (Enter to submit)"
        self.search_input.focus()

    def action_prev_page(self):
        """Go to previous page."""
        if self.page > 1 and not self.is_full_view:
            self.page -= 1
            self.update_table()

    def action_next_page(self):
        """Go to next page."""
        inventory = get_inventory()
        page_count = (len(inventory) + self.page_size - 1) // self.page_size
        if self.page < page_count and not self.is_full_view:
            self.page += 1
            self.update_table()

    def action_full_view(self):
        """Toggle between full inventory and paginated view."""
        self.is_full_view = not self.is_full_view
        self.update_table()

    def action_help(self):
        """Show help screen."""
        self.app.push_screen("HelpScreen")
        
    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self.search_input.focus()
            
    # def add_to_cart(cart, sku, quantity, sale_type="P", discount=0):
    #     inventory = get_inventory()
    #     if sku in inventory:
    #         item = inventory[sku]
    #         if item["stock"] >= quantity:
    #             price = item["price"] * quantity * (1 - discount / 100)
    #             cart_item = {
    #                 "item_id": sku,
    #                 "name": item["name"],
    #                 "quantity": quantity,
    #                 "mode": sale_type,
    #                 "total": price
    #             }
    #             cart.append(cart_item)
    #             return cart_item, sum(i["total"] for i in cart), "Item added."
    #         else:
    #             return None, None, "Not enough stock."
    #     else:
    #         return None, None, "Item not found."