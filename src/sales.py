import json
import os
import uuid
from datetime import datetime

def add_item_to_sale(item_id: str, quantity: int, discount_percent: float = 0.0):
    """Add an item to a sale, checking stock availability and applying discount."""
    with open("data/products.json", "r") as f:
        products = json.load(f)

    if item_id in products:
        item = products[item_id]
        if item["stock"] >= quantity:
            price = item["price"]
            discounted_price = price * (1 - discount_percent / 100)
            total = discounted_price * quantity
            return {
                "id": item_id,
                "name": item["name"],
                "price": price,
                "discount_percent": discount_percent,
                "discounted_price": round(discounted_price, 2),
                "quantity": quantity,
                "total": round(total, 2)
            }
        else:
            return {"error": "Not enough stock!"}
    return {"error": "Item not found!"}


def save_sale(cart: list):
    """Save the sale details to sales.json and write receipt to LaTeX file."""
    with open("data/sales.json", "r") as f:
        sales = json.load(f)

    total = sum(item["total"] for item in cart)
    receipt_id = str(uuid.uuid4())[:8].upper()
    sale = {
        "id": receipt_id,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": cart,
        "total": round(total, 2)
    }
    sales.append(sale)

    with open("data/sales.json", "w") as f:
        json.dump(sales, f, indent=2)

    # Make sure transactions dir exists
    os.makedirs("transactions", exist_ok=True)

    # Generate and save LaTeX receipt
    latex = generate_receipt_latex(sale)
    tex_path = os.path.join("transactions", f"receipt_{receipt_id}.tex")
    with open(tex_path, "w") as f:
        f.write(latex)

    return tex_path


def generate_receipt_latex(sale):
    latex = r"""\documentclass[12pt]{article}
\usepackage{geometry}
\usepackage{graphicx}
\usepackage{tikz}
\usepackage{pgfplots}
\geometry{margin=1in}
\pagestyle{empty}
\begin{document}
\begin{center}
\Huge\bfseries Store Receipt\\
\vspace{0.2cm}
\hrule
\vspace{0.3cm}
\end{center}

\textbf{Receipt ID:} """ + sale["id"] + r""" \\
\textbf{Date:} """ + sale["date"] + r""" \\

\vspace{0.3cm}
\begin{tabular}{|l|r|r|r|r|}
\hline
\textbf{Item} & \textbf{Qty} & \textbf{Price} & \textbf{Disc. \%} & \textbf{Total} \\
\hline
"""

    for item in sale["items"]:
        latex += f"{item['name']} & {item['quantity']} & ${item['price']:.2f} & {item['discount_percent']}\\% & ${item['total']:.2f} \\\\ \\hline\n"

    latex += r"""
\end{tabular}

\vspace{0.5cm}
\begin{flushright}
\textbf{Grand Total:} \quad ${:.2f}
\end{flushright}

\vspace{1cm}
\begin{center}
\begin{tikzpicture}
\draw[black, thick] (0,0) rectangle (6,1);
\foreach \x in {0.2,0.4,...,5.8} {
    \draw[black] (\x,0) -- (\x,1);
}
\end{tikzpicture} \\
\small Receipt Barcode
\end{center}
\end{document}
""".format(sale["total"])

    return latex
