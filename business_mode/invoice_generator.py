"""
Business Mode - Invoice Generator
Invoice creation, calculation, and export in multiple formats.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class InvoiceGenerator:
    """Generate and manage invoices"""
    
    def __init__(self, output_dir: str = './invoices'):
        """Initialize invoice generator"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.invoices = self._load_invoices()
    
    def _load_invoices(self) -> Dict:
        """Load invoices from storage"""
        invoices_file = self.output_dir / 'invoices.json'
        if invoices_file.exists():
            try:
                with open(invoices_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_invoices(self):
        """Save invoices to storage"""
        try:
            invoices_file = self.output_dir / 'invoices.json'
            with open(invoices_file, 'w') as f:
                json.dump(self.invoices, f, indent=2)
        except Exception:
            pass
    
    def create_invoice(self, client_name: str, items: List[Dict], tax_rate: float = 0.0, invoice_number: Optional[str] = None) -> str:
        """Create new invoice"""
        try:
            invoice_id = invoice_number or str(uuid.uuid4())[:8].upper()
            subtotal = sum(item.get('amount', 0) for item in items)
            tax_amount = subtotal * tax_rate
            total = subtotal + tax_amount
            invoice_data = {
                'invoice_id': invoice_id,
                'client_name': client_name,
                'items': items,
                'subtotal': subtotal,
                'tax_rate': tax_rate,
                'tax_amount': tax_amount,
                'total': total,
                'status': 'draft',
                'created_at': datetime.now().isoformat(),
                'due_date': None
            }
            self.invoices[invoice_id] = invoice_data
            self._save_invoices()
            return invoice_id
        except Exception:
            return ''
    
    def get_invoice(self, invoice_id: str) -> Optional[Dict]:
        """Get invoice by ID"""
        return self.invoices.get(invoice_id)
    
    def list_invoices(self, status: Optional[str] = None) -> List[Dict]:
        """List invoices with optional status filter"""
        try:
            invoices = list(self.invoices.values())
            if status:
                invoices = [inv for inv in invoices if inv.get('status') == status]
            return invoices
        except Exception:
            return []
    
    def update_invoice(self, invoice_id: str, **kwargs) -> bool:
        """Update invoice"""
        try:
            if invoice_id not in self.invoices:
                return False
            allowed_fields = ['client_name', 'items', 'tax_rate', 'status', 'due_date']
            for key, value in kwargs.items():
                if key in allowed_fields and key != 'items':
                    self.invoices[invoice_id][key] = value
                elif key == 'items':
                    self.invoices[invoice_id][key] = value
                    subtotal = sum(item.get('amount', 0) for item in value)
                    tax_rate = self.invoices[invoice_id].get('tax_rate', 0)
                    tax_amount = subtotal * tax_rate
                    self.invoices[invoice_id]['subtotal'] = subtotal
                    self.invoices[invoice_id]['tax_amount'] = tax_amount
                    self.invoices[invoice_id]['total'] = subtotal + tax_amount
            self._save_invoices()
            return True
        except Exception:
            return False
    
    def export_invoice(self, invoice_id: str, format: str = 'json') -> bool:
        """Export invoice in specified format"""
        try:
            invoice = self.get_invoice(invoice_id)
            if not invoice:
                return False
            output_file = self.output_dir / f"{invoice_id}.{format}"
            if format == 'json':
                with open(output_file, 'w') as f:
                    json.dump(invoice, f, indent=2)
                return True
            elif format == 'txt':
                with open(output_file, 'w') as f:
                    f.write(self._format_text_invoice(invoice))
                return True
            return False
        except Exception:
            return False
    
    def _format_text_invoice(self, invoice: Dict) -> str:
        """Format invoice as text"""
        lines = ["=" * 60, "INVOICE", "=" * 60, f"Invoice ID: {invoice['invoice_id']}", 
                f"Client: {invoice['client_name']}", f"Created: {invoice['created_at']}", "", "Items:", "-" * 60]
        for item in invoice.get('items', []):
            lines.append(f"{item.get('description', 'Service')}: ${item.get('amount', 0):.2f}")
        lines.extend(["-" * 60, f"Subtotal: ${invoice.get('subtotal', 0):.2f}", 
                     f"Tax ({invoice.get('tax_rate', 0)*100:.1f}%): ${invoice.get('tax_amount', 0):.2f}",
                     f"Total: ${invoice.get('total', 0):.2f}", "=" * 60])
        return "\n".join(lines)
    
    def mark_paid(self, invoice_id: str, payment_date: Optional[str] = None) -> bool:
        """Mark invoice as paid"""
        try:
            if invoice_id not in self.invoices:
                return False
            self.invoices[invoice_id]['status'] = 'paid'
            self.invoices[invoice_id]['paid_at'] = payment_date or datetime.now().isoformat()
            self._save_invoices()
            return True
        except Exception:
            return False
    
    def get_invoice_total(self, invoice_id: str) -> float:
        """Get invoice total amount"""
        invoice = self.get_invoice(invoice_id)
        return invoice.get('total', 0) if invoice else 0
