# NewOldPOS - Terminal Point of Sale

A fast, keyboard-driven terminal POS system built with [Textual](https://github.com/Textualize/textual). 

---

## Features

### Inventory & Cart Management:
- Displays available items with prices and stock levels.
- Quick add-to-cart functionality using keyboard or cursor for selecting inventory items.
- Items can be added to the cart via buttons or key bindings (up/down arrows).
- Key bindings for navigating the inventory and managing the cart.

### Sales Screen with Live Updates:
- Tracks sales with unique sale IDs.
- Automatically updates the inventory when a sale is made.
- Calculates and displays the total cost of the cart.
- Supports discounting and different sale types (Pickup/Delivery).

### Hotkey-driven UI:
- `E` = Edit selected cart item
- `X` = Remove selected cart item
- `F1` = Help/Legend
- `F3` = Go Back
- `F12` = Complete Sale

### Dynamic Terminal Resizing:
- The interface adjusts to different terminal sizes, ensuring proper UI layout.

### Receipt Generation:
- After completing a sale, a receipt is generated and displayed in the console.
- Receipts are saved as PDFs and can be retrieved by searching for a unique sale ID.
- A function is available to search the sales log by sale ID.

### Editable Item Entries:
- Items can be edited by selecting their table rows in the inventory view.

---

## Setup

### Installation

1. **Clone the repository and navigate to the directory:**

    ```bash
    git clone https://github.com/YOUR_USERNAME/newoldpos.git
    cd newoldpos
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python3.10 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    pip install typer
    ```

4. **Run the app:**

    Navigate one level up from `src` to `pos_app` and execute:

    ```bash
    cd pos_app  # Navigate one level up from 'src'
    python -m src.main
    ```

---

## Project Structure

- **`src/`** – Source code for the TUI application
- **`data/`** – Inventory and sales storage (JSON)
- **`requirements.txt`** – Python dependencies

---

## Code Explanation

### 1. **Inventory Module (`inventory.py`)**
- Manages the list of items available for purchase, including item names, prices, and stock levels.
- Quick add-to-cart functionality using buttons or key bindings.
- Edit and remove functionality for items in the inventory.

### 2. **Cart and View Cart App (`view_cart.py`)**
- Displays the cart with quantities and total cost, updating in real-time.
- The grand total is recalculated as items are added or removed.

### 3. **Sales Module (`sales.py`)**
- Tracks sales with a unique sale ID for each transaction.
- Updates the inventory whenever a sale is made.
- Handles the generation of receipts for each sale.

### 4. **Receipt Module (`receipt.py`)**
- Generates and saves receipts in PDF format.
- Receipts can be retrieved using the unique sale ID.

### 5. **Main Application (`main.py`)**
- The entry point that integrates all features into a unified interface.
- Initializes inventory, sales, and cart management functionalities.

---

## Shortcuts

| Key     | Action                        |
|---------|-------------------------------|
| 1       | Go to Sales                   |
| 2       | View Inventory                |
| 3       | Exit App                      |
| F1      | Help / Legend                 |
| F3      | Go Back                       |
| F12     | Complete Sale                 |
| E       | Edit selected cart item       |
| X       | Remove selected cart item     |
| P / D   | Sale Type: Pickup / Delivery  |

---

## Running the App

### 1. **Viewing Inventory**
- Displays all available items in the inventory.
- Users can interact with the inventory by using the keyboard (up/down arrows) or by selecting items with the cursor.
- Items can be quickly added to the cart using key bindings or buttons.

### 2. **View Cart**
- Displays the contents of the shopping cart, including item names, quantities, and total cost.
- The total cost updates automatically as items are added or removed.

### 3. **Making a Sale**
- When a sale is made, a unique sale ID is generated.
- The inventory is updated accordingly, and a receipt is generated for the sale.

### 4. **Generating and Retrieving Receipts**
- After a sale is completed, a receipt is displayed in the console.
- The receipt is saved as a PDF and can be retrieved using the unique sale ID.

### 5. **Search Sales by ID**
- Receipts can be searched by sale ID, allowing you to retrieve information about past transactions.

### 6. **Running the App**
To start the app, use the following command:

```bash
python src/main.py
