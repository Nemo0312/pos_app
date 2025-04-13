import json
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Container, Center
from textual.widgets import Static, Input, Button, DataTable
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.reactive import reactive
from textual.binding import Binding
from textual import events
from pathlib import Path
from rich.text import Text
from textual import on
from main import load_inventory, save_sale
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path
from datetime import datetime
import os

class ReceiptGenerator:
    @staticmethod
    def generate_receipt(sale_data:dict)->str:
        """Generate a formatted receipt from sale data."""
        width = 32
        receipt_lines = [
            "╔" + "═" * (width - 2) + "╗",
            "║{:^{width}}║".format("INVOICE RECEIPT", width=width - 2),
            "╟" + "─" * (width - 2) + "╢",
            "║ Sale #: {:<21}║".format(sale_data['id']),
            "║ Date: {:<23}║".format(sale_data['date']),
            "╟" + "─" * (width - 2) + "╢"
        ]
        #add sales items
        for i in sale_data["items"]:
            name=i['name'][:22]
            name_line="║ {:<29}║".format(name)
            detail_line= "║   {:>2} x ${:<6.2f} ${:>12.2f} ║".format(
                i['quantity'], i['price'], i['total']
            )
            receipt_lines.extend([name_line, detail_line])
        
        #add footer
        receipt_lines.extend([
            "╟" + "─" * (width - 2) + "╢",
            "║ TOTAL: ${:>20.2f} ║".format(sale_data['total']),
            "╚" + "═" * (width - 2) + "╝",
            "",
            "Thank you for your business!",
            "Returns within 14 days with receipt"
        ])
        return "\n".join(receipt_lines)
        
    # def view_pdf(self)-> None:
    @staticmethod
    def generate_pdf_receipt(sale_data: dict, output_dir: str = "data/receipts") -> str:
        """Generate a PDF receipt and return the file path"""
        # Create receipts directory if it doesn't exist
        receipts_dir = Path(output_dir)
        receipts_dir.mkdir(parents=True, exist_ok=True)
        
        # Clean date for filename
        clean_date = sale_data['date'][:10].replace("-", "")
        filename = f"receipt_{sale_data['id']}_{clean_date}.pdf"
        filepath = receipts_dir / filename
        
        # Create PDF
        c = canvas.Canvas(str(filepath), pagesize=letter)
        width, height = letter
        
        # Header
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width/2, height-50, "INVOICE RECEIPT")
        
        # Sale info
        c.setFont("Helvetica", 12)
        c.drawString(100, height-80, f"Sale #: {sale_data['id']}")
        c.drawString(100, height-100, f"Date: {sale_data['date']}")
        c.line(100, height-110, width-100, height-110)
        
        # Items
        y_position = height-130
        for item in sale_data['items']:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(100, y_position, item['name'])
            y_position -= 20
            
            c.setFont("Helvetica", 10)
            item_text = f"{item['quantity']} x ${item['price']:.2f} = ${item['total']:.2f}"
            c.drawString(120, y_position, item_text)
            y_position -= 25
        
        # Total
        c.line(100, y_position-10, width-100, y_position-10)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, y_position-30, f"TOTAL: ${sale_data['total']:.2f}")
        
        # Footer
        c.setFont("Helvetica-Oblique", 10)
        c.drawCentredString(width/2, 50, "Thank you for your business!")
        c.drawCentredString(width/2, 30, "Returns within 14 days with receipt")
        
        c.save()
        return str(filepath)
    
    @staticmethod
    def view_pdf(filepath:str) -> bool:
        """Open the generated PDF receipt."""
        try:
            if os.name == 'nt':
                os.startfile(filepath)
            elif os.name == 'posix':
                os.system(f'open "{filepath}"' if os.uname().sysname == 'Darwin' else f'xdg-open "{filepath}"')
            return True
        except Exception as e:
            print(f"Error opening PDF: {e}")
            return False
        
class ReceiptScreen(Screen):
    BINDINGS = [
        Binding("f3", "app.pop_screen", "Back"),
        Binding('v', 'view_pdf', 'View PDF'),
        Binding('c', 'close', 'Close'),
    ]
    
    def action_close(self) -> None:
        self.app.pop_screen()
        
    def action_app_pop_screen(self) -> None:
        """Close the current screen."""
        self.app.pop_screen()
        
    def action_view_pdf(self) -> None:
        ReceiptGenerator.view_pdf(self.pdf_path)
        
    
        
    def __init__(self, text_receipt:str, pdf_path:str, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.text_receipt = text_receipt
        self.pdf_path = pdf_path
        
        
    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.text_receipt, classes="receipt"),
            Horizontal(
                Button("View PDF", id="view_pdf"),
                # Button("Email Receipt", id="email"),
                Button("Close", id="close"),
                classes="buttons"
            )
        )
        
    def on_button_pressed(self, event: Button.Pressed)->None:
        """Handle button presses in the receipt screen."""
        if event.button.id == "view_pdf":
            ReceiptGenerator.view_pdf(self.pdf_path)
        # elif event.button.id == "email":
        #     self.email_receipt()
        elif event.button.id == "close":
            self.app.pop_screen()
                

