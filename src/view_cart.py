# src/view_cart.py

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static
from textual.containers import Vertical
from rich.text import Text

cart = [
    {"name": "Item 1", "quantity": 2, "total": 20.00},
    {"name": "Item 2", "quantity": 1, "total": 15.50}
]

class CartTotal(Static):
    def on_mount(self):
        """Calculates and updates the total cost of the items in the cart."""
        total = sum(item["total"] for item in cart)  # Sum up the 'total' key in each item
        self.update(Text(f"Grand Total: ${total:.2f}", style="bold green"))


class ViewCartApp(App):
    """The main application for viewing the shopping cart."""
    
    CSS_PATH = None  # You can add a custom CSS path if needed
    BINDINGS = [("q", "quit", "Quit")]  # Press "q" to quit the app

    def compose(self) -> ComposeResult:
        """Compiles the widgets for the app."""
        yield Header()  # App header
        yield Vertical(
            Static("Current Cart", classes="title", style="bold cyan underline"),  # Title
            self.create_table(),  # DataTable showing cart contents
            CartTotal(),  # Cart total widget
        )
        yield Footer()  # App footer

    def create_table(self) -> DataTable:
        """Creates the data table that lists the cart items."""
        table = DataTable(zebra_stripes=True)  # A table with alternating row colors
        table.add_columns("Item", "Quantity", "Total")  # Column names

        if not cart:
            table.add_row("Cart is empty", "", "")  # Message if cart is empty
        else:
            for item in cart:
                # Add each row with the name, quantity, and total price of each item
                table.add_row(
                    item["name"],
                    str(item["quantity"]),
                    f"${item['total']:.2f}"  # Format total as currency
                )

        return table


if __name__ == "__main__":
    app = ViewCartApp()  # Create the app instance
    app.run()  # Run the app
