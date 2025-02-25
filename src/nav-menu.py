import typer
from rich.console import Console
from rich.table import Table
from src.inventory import get_inventory
from src.sales import add_item_to_sale

app = typer.Typer()
console = Console()

def display_menu():
    """Display the main navigation menu."""
    table = Table(title="POS System Menu", show_header=False, style="bold cyan")
    table.add_column("Option", style="magenta")
    table.add_column("Description", style="green")
    
    table.add_row("1", "Process Sale")
    table.add_row("2", "View Inventory")
    table.add_row("3", "Add Item to Sale")
    table.add_row("0", "Exit")
    
    console.clear()
    console.print(table)
    console.print("\n[bold yellow]Select an option (0-3):[/bold yellow] ", end="")

def process_sale():
    """Placeholder for processing a full sale."""
    console.print("[yellow]Sale processing not fully implemented yet.[/yellow]")
    console.print("Enter items via 'Add Item to Sale' first, then finalize here in the future.")
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
    """Interactively add an item to a sale."""
    item_id = console.input("[bold cyan]Enter Item ID: [/bold cyan]")
    try:
        quantity = int(console.input("[bold cyan]Enter Quantity: [/bold cyan]"))
        result = add_item_to_sale(item_id, quantity)
        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]")
        else:
            console.print(f"[green]Added {quantity} x {result['name']} - ${result['total']:.2f}[/green]")
    except ValueError:
        console.print("[red]Error: Quantity must be a number![/red]")
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