import typer
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.align import Align
from rich.panel import Panel
from shutil import get_terminal_size
from src.inventory import get_inventory
from src.sales import add_item_to_sale, save_sale
import time

app = typer.Typer()
console = Console()
cart = []  # Global cart to track items before sale

def show_help():
    """Display the help/legend menu."""
    console.clear()
    width = get_terminal_size().columns
    help_text = Align.center("""
[green]0[/green]: Exit application
[green]1[/green]: Process Sale
[green]2[/green]: View Inventory
[green]3[/green]: Add Item to Sale
[green]4[/green]: Show Help Menu
    """, width)
    console.print(Panel.fit(help_text, title="[bold magenta]Help / Legend Menu[/bold magenta]", border_style="magenta"))
    console.input("\n[dim]Press Enter to return...[/dim]")

def display_menu():
    """Display the main navigation menu."""
    table = Table(title="POS System Menu", show_header=False, style="bold cyan")
    table.add_column("Option", style="magenta", justify="center")
    table.add_column("Description", style="green", justify="center")

    table.add_row("1", "Process Sale")
    table.add_row("2", "View Inventory")
    table.add_row("3", "Add Item to Sale")
    table.add_row("4", "Help / Legend")
    table.add_row("0", "Exit")

    console.clear()
    width = get_terminal_size().columns
    console.print(Align.center(table, width=width))
    console.print("\n[bold yellow]Select an option (0-4):[/bold yellow] ", end="", justify="center")

def process_sale():
    """Process the current cart and save the sale."""
    if not cart:
        console.print("[yellow]Cart is empty![/yellow]", justify="center")
    else:
        table = Table(title="Sale Summary", style="bold green")
        table.add_column("Item", style="cyan", justify="center")
        table.add_column("Quantity", style="magenta", justify="center")
        table.add_column("Total", style="yellow", justify="center")

        total = 0
        for item in cart:
            table.add_row(item["name"], str(item["quantity"]), f"${item['total']:.2f}")
            total += item["total"]

        console.clear()
        width = get_terminal_size().columns
        console.print(Align.center(table, width=width))
        console.print(f"[bold green]Grand Total: ${total:.2f}[/bold green]", justify="center")

        # Save sale to sales.json
        save_sale(cart, total)
        cart.clear()
        console.print("[green]Sale completed and saved![/green]", justify="center")
    console.input("[dim]Press Enter to return...[/dim]")

def view_inventory():
    """Display the current inventory."""
    inventory = get_inventory()
    table = Table(title="Current Inventory", style="bold green")
    table.add_column("ID", style="cyan", justify="center")
    table.add_column("Name", style="green", justify="center")
    table.add_column("Price", style="yellow", justify="center")
    table.add_column("Stock", style="magenta", justify="center")

    for item_id, item in inventory.items():
        table.add_row(item_id, item["name"], f"${item['price']:.2f}", str(item["stock"]))

    console.clear()
    width = get_terminal_size().columns
    console.print(Align.center(table, width=width))
    console.input("[dim]Press Enter to return...[/dim]")

def add_item_interactive():
    """Interactively add an item to the cart."""
    item_id = console.input("[bold cyan]Enter Item ID: [/bold cyan]")
    try:
        quantity = int(console.input("[bold cyan]Enter Quantity: [/bold cyan]"))
        result = add_item_to_sale(item_id, quantity)
        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]", justify="center")
        else:
            cart.append({"item_id": item_id, "name": result["name"], "quantity": quantity, "total": result["total"]})
            console.print(f"[green]Added {quantity} x {result['name']} to cart - ${result['total']:.2f}[/green]", justify="center")
    except ValueError:
        console.print("[red]Error: Quantity must be a number![/red]", justify="center")
    console.input("[dim]Press Enter to return...[/dim]")

def main_menu():
    """Run the main menu loop."""
    while True:
        display_menu()
        choice = console.input("--->").strip()

        if choice == "0":
            console.print("[bold red]Exiting POS System. Goodbye![/bold red]", justify="center")
            break
        elif choice == "1":
            process_sale()
        elif choice == "2":
            view_inventory()
        elif choice == "3":
            add_item_interactive()
        elif choice == "4":
            show_help()
        else:
            console.print("[red]Invalid option! Please select 0-4.[/red]", justify="center")
            console.input("[dim]Press Enter to continue...[/dim]")

@app.command()
def start():
    """Start the POS navigation menu."""
    ascii_art = """
 ___   __       ______       __ __ __       ______       __           ______       ______     ______       ______      
/__\/ /__/\    /_____/\     /_//_//_/\     /_____/\     /_/\         /_____/\     /_____/\   /_____/\     /_____/\     
\::\_\\  \ \   \::::_\/_    \:\:\:\ \    \:::_ \ \    \:\ \        \:::_ \ \    \:::_ \ \  \:::_ \ \    \::::_\/_    
 \:. `-\  \ \   \:\/___/\    \:\:\:\ \    \:\ \ \ \    \:\ \        \:\ \ \ \    \:(_) \ \  \:\ \ \ \    \:\/___/\   
  \:. _    \ \   \::___\/_    \:\:\:\ \    \:\ \ \ \    \:\ \____    \:\ \ \ \    \: ___\/   \:\ \ \ \    \_::._\:\  
   \. \`-\  \ \   \:\_____\    \:\:\:\ \    \:\_\ \ \    \:\/___/\    \:\/.:| |    \ \ \      \:\_\ \ \     /____\:\ 
    \__\/ \__\/    \_____/     \_______\/     \_____\/     \_____/     \____/_/     \_\/       \_____\/     \_____\/ 
                                                                                                                     
    """
    console.clear()
    width = get_terminal_size().columns
    console.print(Align.center(ascii_art, width=width), style="bold blue")
    console.print("[bold yellow]\nWelcome to OldNewPOS - A CLI POS Experience[/bold yellow]", justify="center")
    console.print("\n[italic red]Disclaimer: This software is a prototype and is intended for educational or demonstration purposes only.[/italic red]", justify="center")
    console.input("\n[dim]Press Enter to begin...[/dim]")
    main_menu()

if __name__ == "__main__":
    app()
