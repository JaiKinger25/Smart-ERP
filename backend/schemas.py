from pydantic import BaseModel
from typing import Optional

class RegisterIn(BaseModel):
    name: str
    email: str
    password: str
class LoginIn(BaseModel):
    email: str
    password: str
class CompanyIn(BaseModel):
    name: str
    address: str = ''
    gst_number: str = ''
    financial_year: str = '2026-2027'
    state: str = 'Maharashtra'
    contact: str = ''
class LedgerIn(BaseModel):
    name: str
    ledger_type: str
    mobile: str = ''
    gst_number: str = ''
    address: str = ''
    opening_balance: float = 0
class StockItemIn(BaseModel):
    name: str
    sku: str = ''
    hsn_code: str = ''
    unit: str = 'PCS'
    purchase_price: float = 0
    selling_price: float = 0
    quantity: float = 0
    gst_percent: float = 0
    reorder_level: float = 5
class VoucherIn(BaseModel):
    voucher_type: str
    party_ledger_id: int
    item_id: int
    quantity: float
    rate: float
    narration: str = ''
