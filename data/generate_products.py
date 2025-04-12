import random
from datetime import datetime, timedelta
import json

# Category mapping based on ID range
id_category_map = {
    "1": "Electrical",
    "2": "Woodworking",
    "3": "Hand Tools",
    "4": "Power Tools",
    "5": "Plumbing",
    "6": "HVAC",
    "7": "Automotive"
}

# Sample item names by category
item_names = {
    "Electrical": ["Surge Protector", "Cable Ties (Pack of 100)", "Grounding Rod", "LED Strip (10ft)", "Wire Nuts (Pack of 50)", "Fuse (20A)", "Battery Backup", "Conduit Pipe (5ft)", "Outlet Tester", "Solar Panel Connector"],
    "Woodworking": ["Oak Dowel (1in)", "Wood Filler (4oz)", "Router Bit", "Clamping Square", "Miter Gauge", "Birch Veneer", "Wood Putty", "Drill Guide", "Saw Blade (10in)", "Finishing Wax"],
    "Hand Tools": ["Mallet", "Wire Stripper", "Bolt Cutter", "Chalk Line", "Stud Finder", "Crowbar", "Pipe Cutter", "Rasp File", "Tin Snips", "Socket Wrench"],
    "Power Tools": ["Drill Bit Set", "Oscillating Tool", "Laser Level", "Chain Saw", "Heat Gun", "Impact Wrench", "Tile Cutter", "Bench Grinder", "Cordless Sander", "Rotary Hammer"],
    "Plumbing": ["Pipe Tee", "Drain Snake", "Ball Valve", "Hose Bib", "Pipe Insulation", "Solder Kit", "Toilet Flapper", "Pressure Regulator", "Pipe Threader", "Gasket Set"],
    "HVAC": ["Air Diffuser", "Thermocouple", "Duct Elbow", "Filter Dryer", "Blower Motor", "Capacitor (10uF)", "Vent Damper", "Heat Exchanger", "Freon Gauge", "Condensate Pump"],
    "Automotive": ["Alternator Belt", "Fuel Filter", "Wheel Lug Wrench", "Battery Terminal", "Oil Drain Pan", "Headlight Bulb", "Brake Fluid", "Tire Gauge", "Exhaust Clamp", "Timing Belt"]
}

# Price ranges by category (min, max)
price_ranges = {
    "Electrical": (2.00, 50.00),
    "Woodworking": (0.99, 50.00),
    "Hand Tools": (3.00, 25.00),
    "Power Tools": (20.00, 100.00),
    "Plumbing": (1.50, 45.00),
    "HVAC": (3.00, 95.00),
    "Automotive": (4.00, 90.00)
}

# Function to generate a random date between April 2025 and September 2025
def random_date():
    start_date = datetime(2025, 4, 1)
    end_date = datetime(2025, 9, 30)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")

# Function to distribute total_items randomly across categories
def distribute_items(total_items, num_categories=7):
    base_count = 1
    remaining_items = total_items - num_categories * base_count
    counts = [base_count] * num_categories
    for _ in range(remaining_items):
        counts[random.randint(0, num_categories - 1)] += 1
    return counts

# Function to generate a unique name
def get_unique_name(base_name, category, used_names):
    if f"{category}:{base_name}" not in used_names:
        return base_name
    version = 2
    while True:
        new_name = f"{base_name} (v{version})"
        if f"{category}:{new_name}" not in used_names:
            return new_name
        version += 1

# Load existing data and find last ID per category
try:
    with open("products.json", "r") as f:
        existing_data = json.load(f)
except FileNotFoundError:
    existing_data = {}

# Find the last ID for each category and track used names
last_ids = {prefix: 0 for prefix in id_category_map.keys()}
used_names = set()  # Format: "category:name"
for item_id, item in existing_data.items():
    prefix = item_id[0]
    if prefix in id_category_map:
        last_ids[prefix] = max(last_ids[prefix], int(item_id))
        used_names.add(f"{item['category']}:{item['name']}")

# User-specified total number of new items
total_items = 215  # Change this to your desired total

# Generate random distribution
category_counts = distribute_items(total_items)
print("Category distribution:", dict(zip(id_category_map.values(), category_counts)))

# Generate new items, appending to existing data
new_items = {}
for category_prefix, count in zip(id_category_map.keys(), category_counts):
    category = id_category_map[category_prefix]
    current_id = last_ids[category_prefix]  # Start from last ID in this category
    for _ in range(count):
        current_id += 1
        item_id = str(current_id)
        base_name = random.choice(item_names[category])
        name = get_unique_name(base_name, category, used_names)
        used_names.add(f"{category}:{name}")
        price_min, price_max = price_ranges[category]
        price = round(random.uniform(price_min, price_max), 2)
        stock = random.randint(10, 300)
        if random.random() < 0.2:  # 20% chance of "no shipment"
            next_ship = "no shipment"
            next_ship_qty = 0
        else:
            next_ship = random_date()
            next_ship_qty = random.randint(0, 500)
        
        new_items[item_id] = {
            "category": category,
            "name": name,
            "price": price,
            "stock": stock,
            "next_ship": next_ship,
            "next_ship_qty": next_ship_qty
        }

# Combine existing and new items
combined_data = {**existing_data, **new_items}

# Sort the combined data by ID (ascending order)
sorted_data = dict(sorted(combined_data.items(), key=lambda x: int(x[0])))

# Write sorted data back to products.json
with open("products.json", "w") as f:
    json.dump(sorted_data, f, indent=2)

print(f"Appended {total_items} new items to 'products.json'. New total items: {len(sorted_data)}.")