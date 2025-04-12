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


from textual.app import App, ComposeResult
from textual.containers import Container, Center, Horizontal, Vertical
from textual.widgets import Static, Input, Button, DataTable
from textual.screen import Screen
from textual.reactive import reactive
from textual.binding import Binding
from textual import events
from pathlib import Path
import json
from datetime import datetime
import pyfiglet

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

class SalesScreen(Screen):
    BINDINGS = [
        Binding("f3", "app.pop_screen", "Back"),
        Binding("f1", "help", "Help"),
        Binding("e", "edit_item", "Edit Item"),
        Binding("x", "remove_item", "Remove Item")
    ]

    cart = reactive([])

    def compose(self) -> ComposeResult:
        self.total_display = Static("Total: $0.00", classes="total")
        self.msg_display = Static("", classes="message")
        self.table = DataTable(id="cart-table")
        self.table.add_columns("SKU", "Item Name", "Quantity", "Sale Type", "Price")

        self.input_sku = Input(placeholder="SKU", id="sku")
        self.input_qty = Input(placeholder="QUANTITY", id="qty")
        self.input_type = Input(placeholder="SALE TYPE (P/D)", id="type")
        self.input_discount = Input(placeholder="DISCOUNT (%)", id="discount")

        return [
            Vertical(
                Static(f"[b yellow]NEWOLDPOS SALES TERMINAL[/b yellow]   [green]User: JohnDoe[/green]   [cyan]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/cyan]", classes="header"),
                Static("[dim]Use Arrow Keys to navigate. Press [b]E[/b] to edit, [b]X[/b] to remove. Press [b]F12[/b] to continue.[/dim]", classes="tip"),
                Horizontal(
                    Vertical(
                        Static("[bold]Action:[/bold]", classes="label"),
                        Static("[b]E[/b] - Edit", classes="shortcut"),
                        Static("[b]X[/b] - Remove", classes="shortcut")
                    ),
                    self.table,
                    id="cart-section"
                ),
                Horizontal(
                    self.input_sku,
                    self.input_qty,
                    self.input_type,
                    self.input_discount,
                    id="item-inputs"
                ),
                Horizontal(
                    Button("F1 Help", id="help"),
                    Button("F3 Back", id="back"),
                    Button("F12 Continue", id="finish"),
                    id="nav-buttons"
                ),
                self.total_display,
                self.msg_display,
                id="sales-screen"
            )
        ]

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "finish":
            self.finish_sale()
        elif event.button.id == "help":
            self.app.push_screen(HelpScreen())
        elif event.button.id == "back":
            self.app.pop_screen()

    def add_item(self, sku=None, qty=None, mode=None, discount="0"):
        sku = sku or self.input_sku.value.strip()
        try:
            quantity = int(qty or self.input_qty.value.strip())
            discount = float(self.input_discount.value.strip() or 0)
        except ValueError:
            self.msg_display.update("Invalid quantity or discount!")
            return

        sale_type = (mode or self.input_type.value.strip().upper()) or "P"
        inventory = load_inventory()
        if sku in inventory:
            item = inventory[sku]
            if item["stock"] >= quantity:
                price = item["price"] * quantity * (1 - discount / 100)
                self.cart.append({
                    "item_id": sku,
                    "name": item["name"],
                    "quantity": quantity,
                    "mode": sale_type,
                    "total": price
                })
                self.table.add_row(sku, item["name"], str(quantity), sale_type, f"${price:.2f}")
                total = sum(i["total"] for i in self.cart)
                self.total_display.update(f"Total: ${total:.2f}")
                self.msg_display.update("Item added.")
            else:
                self.msg_display.update("Not enough stock.")
        else:
            self.msg_display.update("Item not found.")

    def action_edit_item(self):
        if self.table.cursor_row is not None:
            item = self.cart[self.table.cursor_row]
            self.input_sku.value = item["item_id"]
            self.input_qty.value = str(item["quantity"])
            self.input_type.value = item.get("mode", "P")
            self.input_discount.value = ""
            self.cart.pop(self.table.cursor_row)
            self.table.remove_row(self.table.cursor_row)

    def action_remove_item(self):
        if self.table.cursor_row is not None:
            self.cart.pop(self.table.cursor_row)
            self.table.remove_row(self.table.cursor_row)
            total = sum(i["total"] for i in self.cart)
            self.total_display.update(f"Total: ${total:.2f}")
            self.msg_display.update("Item removed.")

    def finish_sale(self):
        total = sum(i["total"] for i in self.cart)
        if self.cart:
            save_sale(self.cart, total)
            self.msg_display.update("Sale saved.")
            self.cart.clear()
            self.table.clear()
            self.total_display.update("Total: $0.00")
        else:
            self.msg_display.update("Cart is empty.")

    def action_help(self):
        self.app.push_screen(HelpScreen())


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
