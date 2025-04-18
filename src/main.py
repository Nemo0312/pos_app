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
from inventory import *  # inventory viewing logic is in inventory.py
from rich.text import Text
from textual import on
from sales import *  # sales logic is in sales.py
from returns import *  # returns logic is in returns.py
from returns import ReturnsScreen

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
                Binding("f1", "help", "Help"),]

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

    def action_goto_returns(self):
        self.app.push_screen(ReturnsScreen())  # Transition to ReturnsScreen


class Menu(Screen):
    BINDINGS = [
        Binding("1", "goto_sales", "Go to Sales"),
        Binding("2", "goto_inventory", "View Inventory"),
        Binding("3", "goto_returns", "Go to Returns"),
        Binding("4", "receipt_search", "Search Receipt"),
        
        Binding("5", "quit", "Exit"),
        Binding("f1", "help", "Help"),
        Binding("f3", "back", "Back")
    ]

    def compose(self) -> ComposeResult:
        yield Center(
            Container(
                Static(" [bold cyan]NewOldPOS Terminal[/bold cyan]", classes="title"),
                Button("1. Process Sale", id="sale"),
                Button("2. View Inventory", id="inventory"),
                Button("3. Returns", id="returns"),
                Button("4. Search Receipt", id="receipt"),
                Button("5. Exit", id="exit"),
                id="menu"
            )
        )

    def on_button_pressed(self, event: Button.Pressed):
        btn_id = event.button.id
        if btn_id == "sale":
            self.app.push_screen(SalesScreen())
        elif btn_id == "inventory":
            self.app.push_screen(InventoryScreen())
        elif btn_id == "returns":
            self.app.push_screen(ReturnsScreen())  # Transition to ReturnsScreen
        elif btn_id == "receipt":
            self.app.push_screen(ReceiptSearchScreen())
        elif btn_id == "exit":
            self.app.exit()
        
    def action_goto_sales(self): self.app.push_screen(SalesScreen())
    def action_goto_inventory(self): self.app.push_screen(InventoryScreen())
    def action_goto_returns(self): self.app.push_screen(ReturnsScreen())  # Handle ReturnsScreen transition
    def action_quit(self): self.app.exit()
    def action_help(self): self.app.push_screen(HelpScreen())
    def action_back(self): self.app.pop_screen()
    def action_receipt_search(self): self.app.push_screen(ReceiptSearchScreen())


class HelpScreen(Screen):
    def compose(self) -> ComposeResult:
        help_text = Static(
            "\n[bold cyan]Hotkeys:[/bold cyan]\n"
            "  [green]1[/green] - Go to Sales\n"
            "  [green]2[/green] - View Inventory\n"
            "  [green]3[/green] - Go to Returns\n"
            "  [green]4[/green] - Exit App\n"
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
        width: 24; /*consistent button width*/
        background: #3d2f1e;
        color: lightgoldenrodyellow;
        border: heavy #6e4e2e;
        margin: 1;
        text-align: left; /*text flush left*/
    }
    /* Hover state */
    Button:hover {
    background: #5d4b32;  /* Rich brown with better contrast */
    border: heavy #8a6d46; /* Slightly lighter border */
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
        # Pre-install all screens
        from inventory import InventoryScreen
        from sales import SalesScreen
        from returns import ReturnsScreen  # Import ReturnsScreen

        self.install_screen(InventoryScreen(), "InventoryScreen")
        
        # PLEASE DONT REMOVE THESE LINES
        sales = SalesScreen()
        self.install_screen(sales, "SalesScreen")
        self.push_screen(sales)
        self.pop_screen()
        # sales Screen called and popped to initalize for inventory quick-add to function
        
        self.push_screen(IntroScreen())

if __name__ == "__main__":
    app = POSApp()
    app.run()
