# inventory.py
from textual.containers import Container, Center
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
    page_size = 35  # Number of items per page
    is_full_view = reactive(False)  # New reactive variable to track full view state
    current_inventory = reactive({})  # Track currently displayed inventory
    selected_item_id = reactive(None)  # Track selected item ID
    
    temp_message = reactive("", init=False)  # Temporary message for status updates
    
    def on_mount(self)-> None:
        """Initialize the screen and set up the inventory table."""
        self.update_table()
    
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
    Screen {
        layout: vertical;
    }
    
    /* Left panel - controls */
    .left-panel {
        width: 1fr;
        height: 1fr;
        
        padding: 1;
        padding-top: 0;
    }
    
    /* Right panel - table */
    .right-panel {
        width: 2fr;
        height: 1fr;
        padding: 1;
    }
    
    /* Table styling */
    DataTable {
        width: 1fr;
        height: 1fr;
        border: round yellow;
    }
    
    Button {
        width: 1fr;  /* Buttons now use fractional width */
        min-width: 8;  /* Minimum button width */
        height: 4;
        background: #3d2f1e;
        color: lightgoldenrodyellow;
        border: heavy #6e4e2e;
        margin: 1;
        text-align: center;
        content-align: center top;
    }
    
    /* Input field */
    #search {
        width: 1fr;  /* Fills left panel width */
        margin-bottom: 1;
    }
    
    /* Status message */
    .status {
        height: 3;
        content-align: center middle;
        text-style: bold;
        margin: 1 0;
    }
    
    /* Title styling */
    .title {
        text-align: center;
        color: orange;
        margin-bottom: 1;
    }
    
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
        
    .button-group {
        padding: 1;
        margin: 0;
        
    }

    .button-group > Horizontal {
        margin: 0;
        padding: 1;
        height: auto;
    }

    .button-group Button {
        margin: 0;
    }
    
    
    """

    def compose(self) -> ComposeResult:
        self.table = DataTable()
        self.table.add_columns("ID", "Category", "Name", "Price", "Stock", "Next Shipment", "Incoming Stock")
        self.table.zebra_stripes = True
        self.table.cursor_type = "row"
        self.status = Static("", classes="status")
        self.search_input = Input(placeholder="Search by ID, name, or category (Enter to search)", id="search")
        self.add_to_cart_btn = Button("Add to Cart\n(A)", id="add-to-cart", disabled=True)
        
        self.operations_help = Static(
            """[b]Operations Help[/b]
─────────────────────────────
 [b]Ctrl+D[/b]: Focus Search Bar       
 [b]Select Items[/b]: Up/Down Arrow Keys 
 [b]Full Inventory View[/b]: Toggle with "2" 
 [b]Add to Cart[/b]: "A" after selecting an item               
 [b]Search by Page[/b]: "P", page number and Enter
 [b]Back to Main Menu[/b]: F3 
─────────────────────────────""",
            classes="operations-help"
        )
        self.operations_help.display = False  # Initially hidden

        yield Container(
            Vertical(
                Static(" [bold cyan]NewOldPOS Terminal[/bold cyan]", classes="title"),
                Static("[bold green]Inventory View[/bold green]", classes="title"),
            
            Horizontal(
                #left panel
                Vertical(      
                    self.search_input,
                    Vertical(      
                        Horizontal(
                            Button("Previous\n(-/← )", id="prev", disabled=True),
                            Button("Next\n(+/→ )", id="next", disabled=False),
                        ),
                        Horizontal(
                            self.add_to_cart_btn,
                            Button("Full View\n(2)", id="full"),
                        ),
                        Horizontal(
                            Button("Help\n(F1)", id="help"),       
                        ),
                        
                        classes = "button-group",
                    ),
                    self.operations_help,
                    classes="left-panel"
                ),
                #right panel
                Vertical(
                    # Static("INVENTORY", classes="header"),
                    self.table,
                    self.status,
                    classes="right-panel"    
                ),
            classes="main-container"
            )
        ))
        
    def update_table(self, inventory=None, filtered=False):
        """Update the table with inventory data, either paginated or filtered."""
        inventory = inventory or get_inventory()
        self.current_inventory = inventory
        
        #clear existing rows
        self.table.clear()
        
        # Add columns to the table
        if filtered or self.is_full_view:
            for i, ii in inventory.items():
                self.table.add_row(
                    i, ii["category"], ii["name"], f"${ii['price']:.2f}",
                    str(ii["stock"]), ii.get("next_ship", "N/A"), str(ii.get("next_ship_qty", 0)),
                    key=i # Use the item ID as the key for the row
                )
            #disable next and previous page buttons when in full view/ filtered search
            self.query_one("#prev", Button).disabled = True
            self.query_one("#next", Button).disabled = True
            self.status.update(f"[yellow]Showing {len(inventory)} items (Full View)[/yellow]")
        else:
            # page/item indexing calculations
            items = list(inventory.items())
            item_count = len(items)
            page_count = (item_count + self.page_size - 1) // self.page_size
            start_index = (self.page - 1) * self.page_size
            end_index = min(start_index + self.page_size, item_count)
            
            # Add rows to the table for the current page
            if start_index < item_count and self.page > 0:
                for item_id, item in items[start_index:end_index]:
                    self.table.add_row(
                        item_id, item["category"], item["name"], f"${item['price']:.2f}",
                        str(item["stock"]), item.get("next_ship", "N/A"), str(item.get("next_ship_qty", 0)), key=item_id
                    )
                self.status.update(f"[yellow]Showing items {start_index + 1}-{end_index} of {item_count} (Page {self.page}/{page_count})[/yellow]")
                
                if self.page == 1:# Disable previous button on first page
                    self.query_one("#prev", Button).disabled = True
                else:
                    self.query_one("#prev", Button).disabled = False
                if self.page == page_count: # Disable next button on last page
                    self.query_one("#next", Button).disabled = True
                else:
                    self.query_one("#next", Button).disabled = False
            else:
                # Error message if user tries to access a page out of range
                self.status.update(f"[red]Page {self.page} out of range 1-{page_count}[/red]")
                
                
    @on(DataTable.RowSelected)
    def handle_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in the data table."""
        if event.row_key is None:
            self.selected_item_id = None
            self.query_one("#add-to-cart", Button).disabled = True
            return
            
        self.selected_item_id = str(event.row_key.value)
        
        #disable add to cart button if no item is selected
        self.add_to_cart_btn.disabled = False
        
        #display selected item name as confirmation
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
            # Avoid circular import
            from sales import SalesScreen
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
            
            #debug
            if not input_sku:
                raise AttributeError("Could not find SKU input field in SalesScreen")
            
            # debug
            if not hasattr(sales_screen, 'add_item'):
                raise AttributeError("SalesScreen missing add_item method")
            
            # Prepare input
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
            if self.page == 1: # Disable previous button on first page
                self.query_one("#prev", Button).disabled = True
            self.update_table()
        elif event.button.id == "next" and self.page < page_count and not self.is_full_view:
            self.page += 1
            self.query_one("#prev", Button).disabled = False
            if self.page == page_count: # Disable next button on last page
                self.query_one("#next", Button).disabled = True
            self.update_table()
        elif event.button.id == "full": # Toggle full view
            self.is_full_view = not self.is_full_view
            self.update_table()
        elif event.button.id == "add-to-cart":
            self.action_add_to_cart()

        

    def on_input_submitted(self, event: Input.Submitted):
        """Handle search and page number input."""
        if event.input.id == "search":
            search_term = event.value.strip().lower()
            
            if search_term == "p": #launch page mode
                self.action_page_mode()
                return
        
            inventory = get_inventory()
            if not search_term: 
                self.update_table()
            elif search_term == "2": # Toggle full view
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
                    else: #error message when user enter out of bounds
                        self.status.update(f"[red]Page must be 1-{page_count}[/red]")
                except ValueError: #error message when not a number
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
                if filtered: #update if filtered is found
                    self.update_table(filtered, filtered=True)
                else:
                    self.status.update("[red]No items found![/red]")
            
            #reset and refocus search bar after input submission
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
            if self.page == 1: # Disable previous button on first page
                self.query_one("#prev", Button).disabled = True
            self.update_table()
        

    def action_next_page(self):
        """Go to next page."""
        inventory = get_inventory()
        page_count = (len(inventory) + self.page_size - 1) // self.page_size
        if self.page < page_count and not self.is_full_view:
            self.page += 1
            self.query_one("#prev", Button).disabled = False
            if self.page == page_count: # Disable next button on last page
                self.query_one("#next", Button).disabled = True
            self.update_table()

    def action_full_view(self):
        """Toggle between full inventory and paginated view."""
        self.is_full_view = not self.is_full_view
        self.update_table()

    def action_help(self):
        """Show help screen."""
        self.app.push_screen("HelpScreen")
        
    
    def action_focus_search(self) -> None:
        """Focus on the search input field."""
        self.search_input.focus()

    
    def action_focus_table(self) -> None:
        """Focus the data table and ensure it's scrollable."""
        if not self.table.has_focus:
            self.table.focus()
            
    @on(Button.Pressed, "#help")
    def action_help(self)-> None:  # toggle help display
        self.operations_help.display = not self.operations_help.display
