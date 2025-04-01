import json
from rich.table import Table

def get_inventory():
    """Retrieve the current inventory from products.json."""
    with open("data/products.json", "r") as f:
        return json.load(f)
    
def generate_inventory():
    #Generate table containing inventory information
    inventory = get_inventory()
    table = Table(title="Current Inventory", style="bold green")
    table.add_column("ID", style="cyan")
    table.add_column("Category", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Price", style="yellow")
    table.add_column("Stock", style="magenta")
    table.add_column("Next Shipment", style="blue")
    table.add_column("Incoming Stock", style="magenta")

    for i, ii in inventory.items():
        table.add_row(
            i,
            ii["category"], 
            ii["name"], 
            f"${ii['price']:.2f}", 
            str(ii["stock"]),
            ii["next_ship"],
            str(ii["next_ship_qty"])
            )
        
    return table

def filtered_inventory(filtered_search):
    
    table = Table(title="Your Searches", style="bold green")
    
    table.add_column("ID", style="cyan")
    table.add_column("Category", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Price", style="yellow")
    table.add_column("Stock", style="magenta")
    table.add_column("Next Shipment", style="blue")
    table.add_column("Incoming Stock", style="magenta")
    
    for i, ii in filtered_search.items():
        table.add_row(
            i,
            ii["category"], 
            ii["name"], 
            f"${ii['price']:.2f}", 
            str(ii["stock"]),
            ii["next_ship"],
            str(ii["next_ship_qty"])
            )
        
    return table