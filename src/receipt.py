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
    

        
    def action_app_pop_screen(self) -> None:
        """Close the current screen."""
        self.app.pop_screen()
        
    def action_view_pdf(self) -> None:
        ReceiptGenerator.view_pdf(self.pdf_path)
        
    def action_close(self) -> None:
        self.app.pop_screen()
        
    
        
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
                
class ReceiptSearchScreen(Screen):
    BINDINGS =[
        Binding("f3", "app.pop_screen", "Back"),
        Binding('v', 'view_pdf', 'View PDF'),
        Binding('c', 'close', 'Close'),
    ]
    def action_view_pdf(self) -> None:
        ReceiptGenerator.view_pdf(self.pdf_path)
        
    def action_close(self) -> None:
        self.app.pop_screen()
    
    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_input = Input(placeholder="Search by Sales ID (Enter to search)", id="search-input")
        self.pdf_path = ""
        
    def compose(self) -> ComposeResult:
        yield Container(
            Static("[bold cyan] NewOldPOS Terminal[/bold cyan]", classes="title"),
            Static("Search By Receipt", classes="title"),
            self.search_input,
            Static("", id="receipt-display"),
            Horizontal(
                Button("Search", id="search"),
                Button("View PDF", id="view_pdf", disabled=True),
                Button("Close", id="close"),
                classes="buttons"
            )
        )
        
    @staticmethod
    def find_receipt_by_id(receipt_id: int) -> dict:
        """Search sales.json for a receipt by ID"""
        try:
            with open("data/sales.json", "r") as f:
                sales = json.load(f)
            return next((sale for sale in sales if sale['id'] == receipt_id), None)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
        
    @on(Button.Pressed, "#search")
    @on(Input.Submitted, "#search-input")
    def handle_search(self) -> None:
        """Handle receipt search"""
        receipt_display = self.query_one("#receipt-display")
        search_value = self.search_input.value.strip()
        
        if not search_value:  # Handle empty input
            receipt_display.update("Please enter a receipt ID")
            receipt_display.styles.color = "yellow"
            self.query_one("#view_pdf").disabled = True
            return
        
        try: #search by ID
            receipt_id = int(search_value)
            receipt = self.find_receipt_by_id(receipt_id)
            
            if receipt: # Receipt found
                text_receipt = ReceiptGenerator.generate_receipt(receipt)
                receipt_display.update(text_receipt)
                receipt_display.styles.color = "yellow"
                self.pdf_path = ReceiptGenerator.generate_pdf_receipt(receipt)
                #enable view pdf button
                self.query_one("#view_pdf").disabled = False
            else: # Receipt not found
                receipt_display.update(f"Receipt {receipt_id} not found")
                receipt_display.styles.color = "red"
                self.query_one("#view_pdf").disabled = True
                self.search_input.value = ""
                self.search_input.focus()#refocus are error
            

        except ValueError: #User input NaN
            receipt_display.update(f"Invalid ID {search_value} not recognized.")
            receipt_display.styles.color = "yellow"
            
        self.search_input.value = "" 
        self.query_one("#view_pdf").focus()#focus on view pdf button if success
        


    @on(Button.Pressed, "#view_pdf")
    def view_pdf(self) -> None:
        """View the generated PDF"""
        if self.pdf_path:
            ReceiptGenerator.view_pdf(self.pdf_path)
            

    @on(Button.Pressed, "#close")
    def action_pop_screen(self) -> None:
        """Handle escape key to go back"""
        self.app.pop_screen()   
        
    def action_handle_search(self) -> None:
        """Handle search input"""
        self.handle_search()
        