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
def paginated_inventory(inventory_dict, page,pageSize):
    inventory = list(inventory_dict.items())
    itemCount= len(inventory)
    pageCount= (itemCount + pageSize-1) // pageSize
    startIndex = (page-1)*pageSize
    endIndex = min(startIndex + pageSize, itemCount)
    
    if startIndex>= itemCount or page<1:
        return None, f"Page {page} out of range 1-{pageCount}"
    
    table = Table(title=f"Inventory (Page {page} of {pageCount})", style="bold green")
    table.add_column("ID", style="cyan")
    table.add_column("Category", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Price", style="yellow")
    table.add_column("Stock", style="magenta")
    table.add_column("Next Shipment", style="blue")
    table.add_column("Incoming Stock", style="magenta")
    
    for item_id, item in inventory[startIndex:endIndex]:
        table.add_row(
            item_id,
            item["category"],
            item["name"],
            f"${item['price']:.2f}",
            str(item["stock"]),
            item["next_ship"],
            str(item["next_ship_qty"])
        )
    return table, f"Showing items {startIndex+ 1}-{endIndex} of {itemCount}"