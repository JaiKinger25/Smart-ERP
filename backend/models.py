from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String, nullable=False)
    address = Column(String, default='')
    gst_number = Column(String, default='')
    financial_year = Column(String, default='2026-2027')
    state = Column(String, default='Maharashtra')
    contact = Column(String, default='')

class Ledger(Base):
    __tablename__ = 'ledgers'
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    name = Column(String, nullable=False)
    ledger_type = Column(String, nullable=False)  # Customer, Supplier, Expense, Income, Bank, Cash
    mobile = Column(String, default='')
    gst_number = Column(String, default='')
    address = Column(String, default='')
    opening_balance = Column(Float, default=0)
    current_balance = Column(Float, default=0)

class Unit(Base):
    __tablename__ = 'units'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    name = Column(String, nullable=False)

class StockGroup(Base):
    __tablename__ = 'stock_groups'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    name = Column(String, nullable=False)

class StockItem(Base):
    __tablename__ = 'stock_items'
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    name = Column(String, nullable=False)
    sku = Column(String, default='')
    hsn_code = Column(String, default='')
    unit = Column(String, default='PCS')
    purchase_price = Column(Float, default=0)
    selling_price = Column(Float, default=0)
    quantity = Column(Float, default=0)
    gst_percent = Column(Float, default=0)
    reorder_level = Column(Float, default=5)

class Voucher(Base):
    __tablename__ = 'vouchers'
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    voucher_type = Column(String, nullable=False)  # Sales, Purchase, Payment, Receipt, Journal
    voucher_no = Column(String, nullable=False)
    party_ledger_id = Column(Integer, ForeignKey('ledgers.id'), nullable=True)
    item_id = Column(Integer, ForeignKey('stock_items.id'), nullable=True)
    quantity = Column(Float, default=0)
    rate = Column(Float, default=0)
    amount = Column(Float, default=0)
    tax = Column(Float, default=0)
    total = Column(Float, default=0)
    narration = Column(String, default='')
    created_at = Column(DateTime, default=datetime.utcnow)

class InventoryTransaction(Base):
    __tablename__ = 'inventory_transactions'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    item_id = Column(Integer, ForeignKey('stock_items.id'))
    transaction_type = Column(String) # IN or OUT
    quantity = Column(Float)
    reference = Column(String, default='')
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, nullable=True)
    action = Column(String)
    details = Column(String, default='')
    created_at = Column(DateTime, default=datetime.utcnow)
