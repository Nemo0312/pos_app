import typer
from rich.console import Console
from rich.table import Table
from src.inventory import *
from src.sales import add_item_to_sale, save_sale

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
    
def displayInventoryOnce():
    console.clear()
    console.print(generate_inventory()) # transferred code to inventory.py

def view_inventory():
    """Display the current inventory."""

    displayInventoryOnce()
    m = "\n[blue]Search by name, category, ID \nPress Enter to return to System Menu \nPress 2 for full inventory: [/blue]"
 
    while True:
        user_in = console.input(m).strip().lower()
              
        if not user_in: # User presses Enter without input
            break
        
        if user_in == "2":
            console.clear()
            displayInventoryOnce()
            continue
        
        inventory = get_inventory()
        filtered_search = {}
        
        try: #check if user input is numeric (search by ID)
            user_in_int = int(user_in)
            if user_in_int == 2:
                console.clear()
                displayInventoryOnce()
                continue
            
            filtered_search = {
                item_id:item
                for item_id,item in inventory.items()
                if user_in_int == int(item_id) #matching json key
            }
        except ValueError: #if user input is string (search by name or category)
            filtered_search = {
                item_id: item
                for item_id, item in inventory.items()
                if user_in in item["name"].lower() or user_in in item["category"].lower()
            }
        
        if not filtered_search:
            console.print("[red]No items found![/red]")
            console.input(m)
            continue
        console.clear()
        console.print(filtered_inventory(filtered_search))
    

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