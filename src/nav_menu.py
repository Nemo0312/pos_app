import typer
import json
from rich.console import Console
from rich.table import Table
from src.inventory import get_inventory
from src.sales import add_item_to_sale, save_sale
from src.returns import process_return_update


app = typer.Typer()
console = Console()
cart = []  # Global cart to track items before sale

def display_menu():
    """Display the main navigation menu."""
    table = Table(title="POS System Menu", show_header=False, style="bold cyan")
    table.add_column("Option", style="magenta")
    table.add_column("Description", style="green")
    
    table.add_row("1", "Process Sale")
    table.add_row("2", "View Inventory")
    table.add_row("3", "Add Item to Sale")
    table.add_row("4", "Return Item(s)")
    table.add_row("0", "Exit")
    
    console.clear()
    console.print(table)
    console.print("\n[bold yellow]Select an option (0-3):[/bold yellow] ", end="")

def process_sale():
    """Process the current cart and save the sale."""
    if not cart:
        console.print("[yellow]Cart is empty![/yellow]")
    else:
        table = Table(title="Sale Summary", style="bold green")
        table.add_column("Item", style="cyan")
        table.add_column("Quantity", style="magenta")
        table.add_column("Total", style="yellow")
        
        total = 0
        for item in cart:
            table.add_row(item["name"], str(item["quantity"]), f"${item['total']:.2f}")
            total += item["total"]
        
        console.clear()
        console.print(table)
        console.print(f"[bold green]Grand Total: ${total:.2f}[/bold green]")
        
        # Save sale to sales.json
        save_sale(cart, total)
        cart.clear()
        console.print("[green]Sale completed and saved![/green]")
    console.input("[dim]Press Enter to return...[/dim]")

def view_inventory():
    """Display the current inventory."""
    inventory = get_inventory()
    table = Table(title="Current Inventory", style="bold green")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Price", style="yellow")
    table.add_column("Stock", style="magenta")
    
    for item_id, item in inventory.items():
        table.add_row(item_id, item["name"], f"${item['price']:.2f}", str(item["stock"]))
    
    console.clear()
    console.print(table)
    console.input("[dim]Press Enter to return...[/dim]")

def add_item_interactive():
    """Interactively add an item to the cart."""
    item_id = console.input("[bold cyan]Enter Item ID: [/bold cyan]")
    try:
        quantity = int(console.input("[bold cyan]Enter Quantity: [/bold cyan]"))
        result = add_item_to_sale(item_id, quantity)
        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]")
        else:
            cart.append({"item_id": item_id, "name": result["name"], "quantity": quantity, "total": result["total"]})
            console.print(f"[green]Added {quantity} x {result['name']} to cart - ${result['total']:.2f}[/green]")
    except ValueError:
        console.print("[red]Error: Quantity must be a number![/red]")
    console.input("[dim]Press Enter to return...[/dim]")

def return_items():
    """Handle the return of items from a past sale."""
    try:
        with open("data/sales.json", "r") as f:
            sales = json.load(f)

        if not sales:
            console.print("[yellow]No sales found![/yellow]")
            console.input("[dim]Press Enter to return...[/dim]")
            return

        # Display available receipts
        console.print("[bold cyan]Available Receipts:[/bold cyan]")
        for i, sale in enumerate(sales):
            time_part = sale["date"].split(" ")[1]
            console.print(f"{i+1}. ID: [green]{time_part}[/green] Total: ${sale['total']:.2f}")

        receipt_id = console.input("\n[bold cyan]Enter receipt ID: [/bold cyan]").strip()

        # Find matching receipt by time
        selected_sale = None
        for sale in sales:
            time_part = sale["date"].split(" ")[1]
            if time_part == receipt_id:
                selected_sale = sale
                break

        if not selected_sale:
            console.print("[red]No receipt found with that ID.[/red]")
            console.input("[dim]Press Enter to return...[/dim]")
            return

        # Show receipt details
        table = Table(title=f"Receipt from {selected_sale['date']}", style="bold green")
        table.add_column("Item ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Quantity", style="magenta")
        table.add_column("Total", style="yellow")

        for item in selected_sale["items"]:
            table.add_row(item["item_id"], item["name"], str(item["quantity"]), f"${item['total']:.2f}")

        console.print(table)

        # Begin return process
        returned_items = []
        while True:
            #
            item_id = console.input("[bold cyan]Enter Item ID [/bold cyan]"+"[dim]or type 'c' to complete transaction: [/dim]")
            if item_id.lower() == "c":
                process_return_update(receipt_id, returned_items)
                break

            # Find the item in the selected receipt
            matching_item = next((item for item in selected_sale["items"] if item["item_id"] == item_id), None)

            if matching_item:
                try:
                    qty_to_return = int(console.input("[bold cyan]Enter Quantity: [/bold cyan]"))

                    if 0 < qty_to_return <= matching_item["quantity"]:
                        # Create a returned item record
                        returned_item = {
                            "item_id": item_id,
                            "name": matching_item["name"],
                            "quantity": qty_to_return,
                            "total": round((matching_item["total"] / matching_item["quantity"]) * qty_to_return, 2)
                        }
                        returned_items.append(returned_item)
                        console.print(f"[yellow]Queued {qty_to_return} x {matching_item['name']}[/yellow]")
                    else:
                        console.print("[red]Invalid quantity entered.[/red]")
                except ValueError:
                    console.print("[red]Quantity must be a number![/red]")
            else:
                console.print("[red]Item not found in the selected receipt.[/red]")

        if returned_items:
            console.print("[bold green]Item(s) returned successfully.[/bold green]")
        else:
            console.print("[yellow]No items were returned.[/yellow]")

    except FileNotFoundError:
        console.print("[red]Sales data not found![/red]")
    except json.JSONDecodeError:
        console.print("[red]Error reading sales data.[/red]")

    console.input("[dim]Press Enter to return...[/dim]")


def main_menu():
    """Run the main menu loop."""
    while True:
        display_menu()
        choice = console.input("").strip()
        
        if choice == "0":
            console.print("[bold red]Exiting POS System. Goodbye![/bold red]")
            break
        elif choice == "1":
            process_sale()
        elif choice == "2":
            view_inventory()
        elif choice == "3":
            add_item_interactive()
        elif choice == "4":
            return_items()
        else:
            console.print("[red]Invalid option! Please select 0-3.[/red]")
            console.input("[dim]Press Enter to continue...[/dim]")

@app.command()
def start():
    """Start the POS navigation menu."""
    console.print("[bold blue]Welcome to the POS System![/bold blue]")
    main_menu()

if __name__ == "__main__":
    app()
