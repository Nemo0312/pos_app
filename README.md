# NewOldPOS - Terminal Point of Sale

A fast, keyboard-driven terminal POS system built with [Textual](https://github.com/Textualize/textual).
Inspired by Lowe's Genesis, this CLI tool is focused on efficient workflows using repetition.

## Features

- Inventory & cart management
- Sales screen with live updates
- Hotkey-driven UI: `E` = Edit, `X` = Remove, `F1` = Help, `F3` = Back, `F12` = Checkout
- Dynamic terminal resizing
- Discount support and sale types (Pickup/Delivery)
- Editable item entries using table row selection

## Setup

```bash
# Clone the repo and enter directory
git clone https://github.com/YOUR_USERNAME/newoldpos.git
cd newoldpos

# Create and activate virtual environment
python3.10 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python src/main.py
```

## Files

- `src/` – Source code for the TUI application
- `data/` – Inventory and sales storage (JSON)
- `requirements.txt` – Python dependencies

## Shortcuts

| Key       | Action                        |
|-----------|-------------------------------|
| 1         | Go to Sales                   |
| 2         | View Inventory                |
| 3         | Exit App                      |
| F1        | Help / Legend                 |
| F3        | Go Back                       |
| F12       | Complete Sale                 |
| E         | Edit selected cart item       |
| X         | Remove selected cart item     |
| P / D     | Sale Type: Pickup / Delivery  |

---

Made with ❤️ for terminal workflows.
