# src/view_cart.py


from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static
from textual.containers import Vertical
from rich.text import Text
from src.nav_menu import cart  




class CartTotal(Static):
    def on_mount(self):
        total = sum(item["total"] for item in cart)
        self.update(Text(f"Grand Total: ${total:.2f}", style="bold green"))




class ViewCartApp(App):
    CSS_PATH = None  
    BINDINGS = [("q", "quit", "Quit")]


    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static("Current Cart", classes="title", style="bold cyan underline"),
            self.create_table(),
            CartTotal(),
        )
        yield Footer()


    def create_table(self) -> DataTable:
        table = DataTable(zebra_stripes=True)
        table.add_columns("Item", "Quantity", "Total")


        if not cart:
            table.add_row("Cart is empty", "", "")
        else:
            for item in cart:
                table.add_row(
                    item["name"],
                    str(item["quantity"]),
                    f"${item['total']:.2f}"
                )


        return table




if __name__ == "__main__":
    app = ViewCartApp()
    app.run()
