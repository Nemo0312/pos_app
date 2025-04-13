# inventory.py
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Static, Input, Button
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.binding import Binding
from textual import events, on
from pathlib import Path
import json
from rich.text import Text
from sales import SalesScreen


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
        Binding("2", "full_view", "Toggle Full/Paginated View"),  # Updated description
        Binding("ctrl+d", "focus_search", "Focus Search", priority=True),
        Binding("a", "add_to_cart", "Add to Cart (A)"),
        Binding("up", "focus_table", "Focus Table", show=False),
        Binding("down", "focus_table", "Focus Table", show=False),
        
    ]

    page = reactive(1)
    page_size = 10
    is_full_view = reactive(False)  # New reactive variable to track full view state
    current_inventory = reactive({})  # Track currently displayed inventory
    selected_item_id = reactive(None)  # Track selected item ID
    temp_message = reactive("", init=False)  # Temporary message for status updates
    
    def watch_temp_message(self, message: str) -> None:
        """Handle temporary message updates."""
        if message:
            self.status.update(message)
            # Clear message after 2 seconds
            self.set_timer(2, self.clear_temp_message)
    def clear_temp_message(self) -> None:
        """Clear the temporary message and show current view info."""
        self.temp_message = ""
        self.update_status()
    
    def update_status(self) -> None:
        """Update status with current view information."""
        if self.is_full_view:
            item_count = len(self.current_inventory)
            self.status.update(f"[yellow]Showing {item_count} items (Full View)[/yellow]")
        else:
            items = list(self.current_inventory.items())
            item_count = len(items)
            page_count = (item_count + self.page_size - 1) // self.page_size
            start_index = (self.page - 1) * self.page_size
            end_index = min(start_index + self.page_size, item_count)
            self.status.update(
                f"[yellow]Showing items {start_index + 1}-{end_index} of {item_count} "
                f"(Page {self.page}/{page_count})[/yellow]"
            )
    CSS = """
    DataTable {
        height: 1fr;
        width: 1fr;
        border: round yellow;
    }
    DataTable > .datatable--hover {
        background: $accent;
        color: $text;
    }
    DataTable > .datatable--highlight {
        background: $accent 50%;
        color: $text;
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
        self.table.cursor_type = "row"
        self.status = Static("", classes="status")
        self.search_input = Input(placeholder="Search by ID, name, or category (Enter to search)", id="search")
        self.add_to_cart_btn = Button("Add to Cart (A)", id="add-to-cart", disabled=True)
        self.update_table()

        yield Vertical(
            Static(" [bold cyan]NewOldPOS Terminal[/bold cyan]", classes="title"),
            Static("[bold green]Inventory View[/bold green]", classes="title"),
            self.table,
            self.status,
            self.search_input,
            Horizontal(
                self.add_to_cart_btn,
                Button("Previous", id="prev", disabled=True),
                Button("Next", id="next", disabled=False),
                Button("Full View (2)", id="full"),
                id="controls"
            )
        )

    def update_table(self, inventory=None, filtered=False):
        """Update the table with inventory data, either paginated or filtered."""
        inventory = inventory or get_inventory()
        self.current_inventory = inventory
        self.table.clear()
        if filtered or self.is_full_view:
            for i, ii in inventory.items():
                self.table.add_row(
                    i, ii["category"], ii["name"], f"${ii['price']:.2f}",
                    str(ii["stock"]), ii.get("next_ship", "N/A"), str(ii.get("next_ship_qty", 0)),
                    key=i # Use the item ID as the key for the row
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
                        str(item["stock"]), item.get("next_ship", "N/A"), str(item.get("next_ship_qty", 0)), key=item_id
                    )
                self.status.update(f"[yellow]Showing items {start_index + 1}-{end_index} of {item_count} (Page {self.page}/{page_count})[/yellow]")
            else:
                self.status.update(f"[red]Page {self.page} out of range 1-{page_count}[/red]")
    @on(DataTable.RowSelected)
    def handle_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in the data table."""
        if event.row_key is None:
            self.selected_item_id = None
            self.query_one("#add-to-cart", Button).disabled = True
            return
            
        self.selected_item_id = str(event.row_key.value)
        self.add_to_cart_btn.disabled = False
        item_name = self.current_inventory[self.selected_item_id]["name"]
        self.temp_message = f"Selected: {item_name}"
        
    @on(DataTable.RowHighlighted)
    def handle_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Handle row highlighting (keyboard navigation)."""
        self.handle_row_selected(event) 

    def action_add_to_cart(self) -> None:
        """Add selected item to cart with proper screen initialization."""
        if not self.selected_item_id:
            self.temp_message = "[red]No item selected![/red]"
            return
        
        try:
            # # Get the SalesScreen class (not instance)
            from sales import SalesScreen
            
            # # Create a new instance if needed
            if not self.app.is_screen_installed("SalesScreen"):
                self.app.install_screen(SalesScreen(), "SalesScreen")
            
            # Get the screen instance
            sales_screen = self.app.get_screen("SalesScreen")
            
            # Verify we can access the screen's widgets
            if not hasattr(sales_screen, 'query_one'):
                raise AttributeError("SalesScreen not properly initialized")
            
            # Get the input_sku widget - wait for it to be available
            input_sku = None
            for _ in range(5):  # Try a few times
                input_sku = sales_screen.query_one("#sku-input", Input)
                if input_sku:
                    break
                self.app.process_events()  # Allow the screen to process events
            
            if not input_sku:
                raise AttributeError("Could not find SKU input field in SalesScreen")
            
            # Verify add_item method exists
            if not hasattr(sales_screen, 'add_item'):
                raise AttributeError("SalesScreen missing add_item method")
            
            # Prepare the input
            selected_item = self.current_inventory[self.selected_item_id]
            sku_input = f"{self.selected_item_id}.1"  # Default quantity of 1
            
            # Set the input and trigger add_item
            input_sku.value = sku_input
            sales_screen.add_item()
            
            self.temp_message = f"[green]Added {selected_item['name']} to cart[/green]"
            
        except Exception as e:
            self.temp_message(f"[red]Error adding to cart: {str(e)}[/red]")

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
        elif event.button.id == "add-to-cart":
            self.action_add_to_cart()

        

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
            if self.page == 1:
                self.query_one("#prev", Button).disabled = True
            self.update_table()
        

    def action_next_page(self):
        """Go to next page."""
        inventory = get_inventory()
        page_count = (len(inventory) + self.page_size - 1) // self.page_size
        if self.page < page_count and not self.is_full_view:
            self.page += 1
            self.query_one("#prev", Button).disabled = False
            if self.page == page_count:
                self.query_one("#next", Button).disabled = True
            self.update_table()

    def action_full_view(self):
        """Toggle between full inventory and paginated view."""
        self.is_full_view = not self.is_full_view
        self.update_table()

    def action_help(self):
        """Show help screen."""
        self.app.push_screen("HelpScreen")
        
    # async def on_key(self, event: events.Key) -> None:
    #     if event.key == "enter":
    #         self.search_input.focus()
    
    def action_focus_search(self) -> None:
        """Focus on the search input field."""
        self.search_input.focus()

    
    def action_focus_table(self) -> None:
        """Focus the data table and ensure it's scrollable."""
        if not self.table.has_focus:
            self.table.focus()

    
