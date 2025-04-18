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
#### Many keybindings that streamline processes:
- `F1` = Help/Legend
- `F3` = Go Back
- `F12` = Complete Sale
- `ctrl` + `z` = undo
- ...

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
   git clone https://github.com/Nemo0312/pos_app.git
   cd pos_app
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3.10 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   python -m src.main
   ```

### Docker Setup

To run the application in a Docker container, follow these steps:

1. **Ensure Docker is installed** on your system. [Install Docker](https://docs.docker.com/get-docker/) if needed.

2. **Build the Docker image**:
   From the repository root (where the `Dockerfile` is located), run:
   ```bash
   docker build -t pos_app .
   ```

3. **Run the container**:
   To run the application interactively (required for the terminal UI), use:
   ```bash
   docker run -it pos_app
   ```

4. **Persist data with a volume**:
   To ensure the `data/` directory (used for JSON storage) persists, mount a volume:
   ```bash
   docker run -it -v /path/to/host/data:/app/data pos_app
   ```
   Replace `/path/to/host/data` with a directory on your host machine (e.g., `/home/user/pos_data`).

**Note**: The `Dockerfile` is included in the repository root and configures the Python 3.10 environment with all dependencies.

---

## Project Structure

- **`src/`** – Source code for the TUI application
- **`data/`** – Inventory and sales storage (JSON)
- **`requirements.txt`** – Python dependencies
- **`Dockerfile`** – Docker configuration for containerization

---

## Code Explanation

### 1. **Inventory Module (`inventory.py`)**
#### Users can easily view the current/incoming inventory through the inventory module. This module supports rapid navigation with keybindings, filter searches whilst allowing users to use their cursor for an organic and dynamic experience. Users can filter search by name, ID, and category. The module also supports a quick-add function where they can add items to their live cart directly from the inventory module.

  ![alt text](/pics/image-1.png)
- Overview of Commands

| Command  | Action   |
| ---- | ------ |
| `←` `→` <br />`-` `+` <br />`Previous` `Next` Buttons | Move between pages |
|`2` <br /> `Full View` Button| Toggle Full/Page view |
|`↑` `↓`<br/> Cursor| Select Items|
| `p` + number and Enter <br/>`Page` Button | Move to page number   |
| `a` <br/> `Add to Cart` Button | Quick-add Selected Item to Cart     |
|`ctrl` + `d`|Focus Search Bar|

### 2. **Sales Module with Live Cart  (`sales.py`)**
#### Users can add items to a live cart via SKU numbers. This module supports the adding of multiple quantities via the SKU.QTY processing capabilities as seen below. Cart item quantities can be easily edited or removed. The cart always shows real-time status of cart items, quantities, subtotal(s), and total. 

![alt text](/pics/image.png)
- Tracks sales with a unique sale ID for each transaction.
- Updates the inventory whenever a sale is made.
- Handles the generation of receipts for each sale.
- Overview of Commands

| Command  | Action   |
| - | - |
|`SKU`.`QTY`<br/> i.e. 1011.5| Add Item * Quantity<br/> Default is 1 if no quantity specified|
|`Select item`| Focus Edit Quantity Bar|
|`d`<br/> `-`<br/>`Delete Item` Button|Remove item from cart|
|`new quantity` + `Enter`<br/>`Update Qty` Button|Update Quantity|
|`ctrl` + `z`<br/>`Undo Last` Button|Undo last action|
|`F12`<br/>`Complete Sale` Button|Check out Cart|
|`F4` <br/>`Print Receipt` Button|Generates Receipt Screen|

### 3. **Receipt Module (`receipt.py`)**
#### Integrated as the last step of the sales pipeline, users can quickly view their receipt as plaintext or download a pdf-copy. This module further supports archival searches as past sales transactions can be retrieved via their unique Sales ID.

![alt text](/pics/image-3.png)

- Overview of Commands

| Command  | Action   |
| - | - |
|`v`|Download and view PDF|
|`c`|Close Module|

### 4. **Main Application (`main.py`)**
- The entry point that integrates all features into a unified interface.
- Initializes inventory, sales, and cart management functionalities.

---

## Shortcuts

| Key   | Action                       |
| ------- | ------------------------------ |
| 1     | Go to Sales                  |
| 2     | View Inventory               |
| 3     | Exit App                     |
| F1    | Help / Legend                |
| F3    | Go Back                      |
| F5    | Search Receipt               |
| F12   | Complete Sale                |
| E     | Edit selected cart item      |
| X     | Remove selected cart item    |
| P / D | Sale Type: Pickup / Delivery |

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
python -m src.main
```

---

## Running with Docker
To run the app using Docker, follow the **Docker Setup** section above. The Docker image encapsulates the Python environment and dependencies, ensuring consistency across systems. Use the volume option to persist data stored in the `data/` directory.

```

### Changes Made
1. **Updated Repository URL**: Changed the `git clone` URL to `https://github.com/Nemo0312/pos_app.git` to match your provided link.
2. **Added Docker Setup Section**: Included instructions for building and running the Docker image, with details on persisting data using volumes.
3. **Updated Project Structure**: Added `Dockerfile` to the list of files in the **Project Structure** section.
4. **Added Running with Docker Section**: Included a brief note at the end to cross-reference the Docker setup for users interested in containerized execution.
5. **Simplified Run Command**: Removed the `cd pos_app` instruction in the non-Docker setup, as it's unnecessary if the user is already in the repository root after cloning.
6. **Maintained Consistency**: Ensured the formatting and style match the original README, with clear sections and code blocks for commands.

### Providing a Download
Since I cannot directly upload files to your GitHub repository or provide a direct download link through this interface, I'll offer two options for you to obtain the updated README:

#### Option 1: Copy and Paste
1. Copy the markdown content above.
2. Open your repository's `README.md` file in a text editor or GitHub's online editor.
3. Replace the existing content with the copied content.
4. Commit the changes to your repository.

#### Option 2: Manual Download
1. Copy the markdown content above into a text editor on your local machine.
2. Save the file as `README.md`.
3. Push the updated file to your GitHub repository using:
   ```bash
   git add README.md
   git commit -m "Update README with Docker instructions"
   git push origin main
   ```

#### Option 3: GitHub Instructions
If you prefer, I can provide step-by-step instructions to update the README directly on GitHub:
1. Navigate to your repository: [https://github.com/Nemo0312/pos_app](https://github.com/Nemo0312/pos_app).
2. Click on `README.md` in the repository root.
3. Click the pencil icon to edit the file.
4. Paste the updated markdown content (from above) into the editor.
5. Scroll to the bottom, enter a commit message (e.g., "Add Docker setup to README"), and click "Commit changes."

### Additional Notes
- **Dockerfile Requirement**: Ensure you have a `Dockerfile` in your repository root with the content provided in the previous response (repeated here for convenience):
  ```dockerfile
  FROM python:3.10-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY . .
  CMD ["python", "src/main.py"]
  ```

