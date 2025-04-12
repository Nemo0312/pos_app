from textual.app import App, ComposeResult
from textual.containers import Container, Center
from textual.widgets import Static, Input, Button, DataTable
from textual.screen import Screen
from textual.reactive import reactive
from textual.binding import Binding
from textual import events
from pathlib import Path
import json
from datetime import datetime
import pyfiglet
from inventory import * #inventory viewing logic is in inventory.py
from rich.text import Text
from textual import on
from sales import * #sales logic is in sales.py

DATA_PATH = Path(__file__).parent.parent / "data"
PRODUCTS_FILE = DATA_PATH / "products.json"
SALES_FILE = DATA_PATH / "sales.json"

def load_inventory():
    with open(PRODUCTS_FILE) as f:
        return json.load(f)

def save_sale(items, total):
    with open(SALES_FILE) as f:
        sales = json.load(f)
    sale = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": items,
        "total": total
    }
    sales.append(sale)
    with open(SALES_FILE, "w") as f:
        json.dump(sales, f, indent=2)

class IntroScreen(Screen):
    BINDINGS = [Binding("f3", "app.pop_screen", "Back"),
                Binding("f1", "help", "Help")]

    def compose(self) -> ComposeResult:
        banner = pyfiglet.figlet_format("NewOldPOS")
        yield Center(
            Container(
                Static(banner, classes="ascii"),
                Static(
                    "[bold yellow]Welcome to NewOldPOS[/bold yellow]\n\n"
                    "[dim]Prototype software intended for demonstration only.[/dim]\n\n"
                    "[green]Press any key to begin...[/green]",
                    classes="message"
                ),
                id="intro"
            )
        )

    async def on_key(self, event: events.Key):
        self.app.pop_screen()
        self.app.push_screen(Menu())

    def action_help(self):
        self.app.push_screen(HelpScreen())

class Menu(Screen):
    BINDINGS = [
        Binding("1", "goto_sales", "Go to Sales"),
        Binding("2", "goto_inventory", "View Inventory"),
        Binding("3", "quit", "Exit"),
        Binding("f1", "help", "Help"),
        Binding("f3", "back", "Back")
    ]

    def compose(self) -> ComposeResult:
        yield Center(
            Container(
                Static("\ud83d\udccb [bold cyan]NewOldPOS Terminal[/bold cyan]", classes="title"),
                Button("1. Process Sale", id="sale"),
                Button("2. View Inventory", id="inventory"),
                Button("3. Exit", id="exit"),
                id="menu"
            )
        )

    def on_button_pressed(self, event: Button.Pressed):
        btn_id = event.button.id
        if btn_id == "sale":
            self.app.push_screen(SalesScreen())
        elif btn_id == "inventory":
            self.app.push_screen(InventoryScreen())
        elif btn_id == "exit":
            self.app.exit()

    def action_goto_sales(self): self.app.push_screen(SalesScreen())
    def action_goto_inventory(self): self.app.push_screen(InventoryScreen())
    def action_quit(self): self.app.exit()
    def action_help(self): self.app.push_screen(HelpScreen())
    def action_back(self): self.app.pop_screen()

# class InventoryScreen(Screen):
#     BINDINGS = [Binding("f3", "app.pop_screen", "Back"),
#                 Binding("f1", "help", "Help")]

#     def compose(self) -> ComposeResult:
#         inventory = load_inventory()
#         table = DataTable()
#         table.add_columns("SKU", "Name", "Price", "Stock")
#         for sku, item in inventory.items():
#             table.add_row(sku, item["name"], f"${item['price']:.2f}", str(item["stock"]))
#         yield Center(
#             Container(
#                 Static("[bold green]Inventory View[/bold green]", expand=True),
#                 table
#             )
#         )

#     def action_help(self): self.app.push_screen(HelpScreen())


# class SalesScreen(Screen):
#     BINDINGS = [
#         Binding("f3", "app.pop_screen", "Back"),
#         Binding("f1", "help", "Help"),
#         Binding("enter", "add_item", "Add Item"),
#     ]

#     cart = reactive([])

#     def compose(self) -> ComposeResult:
#         self.cart_table = DataTable(id="cart-table")
#         self.cart_table.add_columns("SKU", "Name", "Qty", "Price")
        
#         self.input_sku = Input(placeholder="Scan or enter SKU", id="sku-input")
#         self.message = Static("", id="message")
        
#         # Wrap the Vertical container in a list
#         yield Vertical(
#             Horizontal(
#                 Vertical(
#                     Static("ADD ITEM", classes="header"),
#                     self.input_sku,
#                     self.message,
#                     Button("Complete Sale", id="finish", variant="success"),
#                     classes="input-panel"
#                 ),
#                 Vertical(
#                     Static("CART", classes="header"),
#                     self.cart_table,
#                     classes="cart-panel"
#                 ),
#             )
#         )

#     def on_mount(self) -> None:
#         self.input_sku.focus()
        

#     @on(Input.Submitted, "#sku-input")
#     def add_item(self) -> None:
#         input_text = self.input_sku.value.strip()
#         if not input_text:
#             self.message.update("Please enter a SKU")
#             return
        
#         # Split input into SKU and quantity (default quantity is 1)
#         if '.' in input_text:
#             try:
#                 sku, quantity_str = input_text.split('.')
#                 quantity = int(quantity_str)
#                 if quantity <= 0:
#                     self.message.update("Quantity must be positive")
#                     return
#             except ValueError:
#                 self.message.update("Invalid quantity format (use SKU.QUANTITY)")
#                 return
#         else:
#             sku = input_text
#             quantity = 1
            
#         inventory = load_inventory()
#         if sku not in inventory:
#             self.message.update(f"SKU {sku} not found")
#             return
            
#         item = inventory[sku]
        
#         # Check if item already exists in cart
#         existing_index = next((i for i, x in enumerate(self.cart) if x["sku"] == sku), None)
        
#         if existing_index is not None:
#             # Update existing item
#             self.cart[existing_index]["quantity"] += quantity
#             self.cart[existing_index]["total"] += item["price"] * quantity
#         else:
#             # Add new item
#             self.cart.append({
#                 "sku": sku,
#                 "name": item["name"],
#                 "quantity": quantity,
#                 "price": item["price"],
#                 "total": item["price"] * quantity
#             })
        
#         # This will trigger watch_cart() automatically
#         # self.cart = self.cart.copy()  # Force reactive update
#         self.watch_cart()
        
#         self.input_sku.value = ""
#         self.message.update(f"Added {item['name']}")
#         self.input_sku.focus()

#     def watch_cart(self) -> None:
#         """Automatically called when cart changes"""
#         self.cart_table.clear()
        
        
#        # Create a dictionary to combine duplicate SKUs
#         combined_items = {}
#         for item in self.cart:
#             if item["sku"] in combined_items:
#                 combined_items[item["sku"]]["quantity"] += item["quantity"]
#                 combined_items[item["sku"]]["total"] += item["total"]
#             else:
#                 combined_items[item["sku"]] = item.copy()
        
#         # Display the combined items
#         for sku, item in combined_items.items():
#             self.cart_table.add_row(
#                 sku,
#                 item["name"],
#                 str(item["quantity"]),
#                 f"${item['total']:.2f}"
#             )
        
#         # Add total row if cart has items
#         if combined_items:
#             total = sum(item["total"] for item in combined_items.values())
#             self.cart_table.add_row(
#                 "", 
#                 "", 
#                 Text("Total:", style="bold"), 
#                 Text(f"${total:.2f}", style="bold green")
#             )

#     @on(Button.Pressed, "#finish")
#     def complete_sale(self) -> None:
#         if not self.cart:
#             self.message.update("Cart is empty")
#             return
            
#         total = sum(item["price"] for item in self.cart)
#         save_sale(self.cart, total)
#         self.message.update(f"Sale completed! Total: ${total:.2f}")
#         self.cart = []  # Clear cart (triggers watch_cart)
#         self.input_sku.focus()


class HelpScreen(Screen):
    def compose(self) -> ComposeResult:
        help_text = Static(
            "\n[bold cyan]Hotkeys:[/bold cyan]\n"
            "  [green]1[/green] - Go to Sales\n"
            "  [green]2[/green] - View Inventory\n"
            "  [green]3[/green] - Exit App\n"
            "  [green]F1[/green] - Help Menu (Anywhere)\n"
            "  [green]F3[/green] - Go Back (Universal)\n"
        )
        yield Center(
            Container(
                Static("[bold yellow]Help / Legend[/bold yellow]", expand=True),
                help_text
            )
        )

    def on_key(self, event: events.Key):
        self.app.pop_screen()

class POSApp(App):
    TITLE = "NewOldPOS"
    CSS = """
    Screen {
        align: center middle;
        background: #1e1e1e;
        color: wheat;
    }
    Static.title {
        text-align: center;
        color: orange;
        margin-bottom: 1;
    }
    .ascii {
        color: gold;
        text-align: center;
        text-style: bold;
    }
    .message {
        color: tan;
        text-align: center;
        padding: 1 2;
    }
    Button {
        background: #3d2f1e;
        color: lightgoldenrodyellow;
        border: heavy #6e4e2e;
        margin: 1;
    }
    Input {
        border: round #e8c28c;
        padding: 0 1;
    }
    DataTable {
        border: round yellow;
    }
    """

    def on_mount(self):
        self.push_screen(IntroScreen())

if __name__ == "__main__":
    app = POSApp()
    app.run()
