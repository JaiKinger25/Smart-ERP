from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO
from datetime import datetime
import openpyxl
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from database import Base, engine, get_db
from models import User, Company, Ledger, StockItem, Voucher, InventoryTransaction, AuditLog
from schemas import RegisterIn, LoginIn, CompanyIn, LedgerIn, StockItemIn, VoucherIn
from auth import hash_password, verify_password, create_token, read_token

Base.metadata.create_all(bind=engine)
app = FastAPI(title='SmartERP Guideline MVP')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

def current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(401, 'Not authenticated')
    data = read_token(authorization.replace('Bearer ', ''))
    if not data:
        raise HTTPException(401, 'Invalid token')
    user = db.query(User).filter(User.id == data['user_id']).first()
    if not user:
        raise HTTPException(401, 'User not found')
    return user

@app.on_event('startup')
def seed_admin():
    db = next(get_db())
    if not db.query(User).filter(User.email == 'admin@smarterp.com').first():
        u = User(name='SmartERP Admin', email='admin@smarterp.com', password_hash=hash_password('admin123'))
        db.add(u); db.commit(); db.refresh(u)
        c = Company(user_id=u.id, name='Demo Trading Company', address='Pune', gst_number='27ABCDE1234F1Z5')
        db.add(c); db.commit(); db.refresh(c)
        db.add(Ledger(company_id=c.id, name='Cash', ledger_type='Cash', current_balance=10000))
        db.add(Ledger(company_id=c.id, name='Rahul Customer', ledger_type='Customer', mobile='9999999999', current_balance=0))
        db.add(Ledger(company_id=c.id, name='ABC Supplier', ledger_type='Supplier', mobile='8888888888', current_balance=0))
        db.add(StockItem(company_id=c.id, name='Laptop', sku='LAP001', hsn_code='8471', unit='PCS', purchase_price=45000, selling_price=52000, quantity=10, gst_percent=18))
        db.add(StockItem(company_id=c.id, name='Mouse', sku='MOU001', hsn_code='8471', unit='PCS', purchase_price=300, selling_price=500, quantity=50, gst_percent=18))
        db.commit()
    db.close()

@app.get('/')
def root(): return {'message': 'SmartERP API running'}

@app.post('/auth/register')
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, 'Email already registered')
    u = User(name=data.name, email=data.email, password_hash=hash_password(data.password))
    db.add(u); db.commit(); db.refresh(u)
    return {'message': 'Registered successfully', 'token': create_token(u.id), 'user': {'id': u.id, 'name': u.name, 'email': u.email}}

@app.post('/auth/login')
def login(data: LoginIn, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email == data.email).first()
    if not u or not verify_password(data.password, u.password_hash):
        raise HTTPException(401, 'Invalid email or password')
    return {'message': 'Login successful', 'token': create_token(u.id), 'user': {'id': u.id, 'name': u.name, 'email': u.email}}

@app.get('/companies')
def companies(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.query(Company).filter(Company.user_id == user.id).all()

@app.post('/companies')
def create_company(data: CompanyIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    count = db.query(Company).filter(Company.user_id == user.id).count()
    if count >= 5: raise HTTPException(400, 'Maximum 5 companies allowed')
    c = Company(user_id=user.id, **data.model_dump())
    db.add(c); db.commit(); db.refresh(c)
    return c

@app.put('/companies/{company_id}')
def update_company(company_id:int, data:CompanyIn, user:User=Depends(current_user), db:Session=Depends(get_db)):
    c = db.query(Company).filter(Company.id==company_id, Company.user_id==user.id).first()
    if not c: raise HTTPException(404,'Company not found')
    for k,v in data.model_dump().items(): setattr(c,k,v)
    db.commit(); db.refresh(c); return c

@app.delete('/companies/{company_id}')
def delete_company(company_id:int, user:User=Depends(current_user), db:Session=Depends(get_db)):
    c = db.query(Company).filter(Company.id==company_id, Company.user_id==user.id).first()
    if not c: raise HTTPException(404,'Company not found')
    db.delete(c); db.commit(); return {'message':'Company deleted'}

@app.get('/dashboard/{company_id}')
def dashboard(company_id:int, user:User=Depends(current_user), db:Session=Depends(get_db)):
    sales = db.query(Voucher).filter(Voucher.company_id==company_id, Voucher.voucher_type=='Sales').all()
    purchases = db.query(Voucher).filter(Voucher.company_id==company_id, Voucher.voucher_type=='Purchase').all()
    items = db.query(StockItem).filter(StockItem.company_id==company_id).all()
    ledgers = db.query(Ledger).filter(Ledger.company_id==company_id).all()
    return {
        'total_sales': sum(v.total for v in sales),
        'total_purchases': sum(v.total for v in purchases),
        'stock_items': len(items),
        'ledgers': len(ledgers),
        'low_stock': [i for i in items if i.quantity <= i.reorder_level]
    }

@app.get('/ledgers/{company_id}')
def list_ledgers(company_id:int, user:User=Depends(current_user), db:Session=Depends(get_db)):
    return db.query(Ledger).filter(Ledger.company_id==company_id).all()
@app.post('/ledgers/{company_id}')
def add_ledger(company_id:int, data:LedgerIn, user:User=Depends(current_user), db:Session=Depends(get_db)):
    l = Ledger(company_id=company_id, current_balance=data.opening_balance, **data.model_dump())
    db.add(l); db.commit(); db.refresh(l); return l
@app.delete('/ledgers/{ledger_id}')
def del_ledger(ledger_id:int, user:User=Depends(current_user), db:Session=Depends(get_db)):
    l=db.query(Ledger).filter(Ledger.id==ledger_id).first()
    if not l: raise HTTPException(404,'Ledger not found')
    db.delete(l); db.commit(); return {'message':'Deleted'}

@app.get('/items/{company_id}')
def list_items(company_id:int, user:User=Depends(current_user), db:Session=Depends(get_db)):
    return db.query(StockItem).filter(StockItem.company_id==company_id).all()
@app.post('/items/{company_id}')
def add_item(company_id:int, data:StockItemIn, user:User=Depends(current_user), db:Session=Depends(get_db)):
    i = StockItem(company_id=company_id, **data.model_dump())
    db.add(i); db.commit(); db.refresh(i); return i
@app.delete('/items/{item_id}')
def del_item(item_id:int, user:User=Depends(current_user), db:Session=Depends(get_db)):
    i=db.query(StockItem).filter(StockItem.id==item_id).first()
    if not i: raise HTTPException(404,'Item not found')
    db.delete(i); db.commit(); return {'message':'Deleted'}

@app.get('/vouchers/{company_id}')
def list_vouchers(company_id:int, user:User=Depends(current_user), db:Session=Depends(get_db)):
    return db.query(Voucher).filter(Voucher.company_id==company_id).order_by(Voucher.id.desc()).all()
@app.post('/vouchers/{company_id}')
def add_voucher(company_id:int, data:VoucherIn, user:User=Depends(current_user), db:Session=Depends(get_db)):
    item = db.query(StockItem).filter(StockItem.id==data.item_id, StockItem.company_id==company_id).first()
    ledger = db.query(Ledger).filter(Ledger.id==data.party_ledger_id, Ledger.company_id==company_id).first()
    if not item or not ledger: raise HTTPException(404, 'Item or ledger not found')
    amount = data.quantity * data.rate
    tax = amount * item.gst_percent / 100
    total = amount + tax
    no = f"{data.voucher_type[:3].upper()}-{db.query(Voucher).filter(Voucher.company_id==company_id).count()+1:04d}"
    if data.voucher_type == 'Sales':
        if item.quantity < data.quantity: raise HTTPException(400, 'Not enough stock')
        item.quantity -= data.quantity
        ledger.current_balance += total
        tx_type='OUT'
    elif data.voucher_type == 'Purchase':
        item.quantity += data.quantity
        ledger.current_balance -= total
        tx_type='IN'
    else:
        tx_type='ADJ'
    v = Voucher(company_id=company_id, voucher_type=data.voucher_type, voucher_no=no, party_ledger_id=data.party_ledger_id, item_id=data.item_id, quantity=data.quantity, rate=data.rate, amount=amount, tax=tax, total=total, narration=data.narration)
    db.add(v); db.commit(); db.refresh(v)
    db.add(InventoryTransaction(company_id=company_id, item_id=item.id, transaction_type=tx_type, quantity=data.quantity, reference=no))
    db.add(AuditLog(company_id=company_id, action=f'{data.voucher_type} voucher created', details=no))
    db.commit(); return v

@app.get('/reports/{company_id}')
def reports(company_id:int, user:User=Depends(current_user), db:Session=Depends(get_db)):
    ledgers=db.query(Ledger).filter(Ledger.company_id==company_id).all()
    items=db.query(StockItem).filter(StockItem.company_id==company_id).all()
    vouchers=db.query(Voucher).filter(Voucher.company_id==company_id).all()
    return {
        'trial_balance': [{'ledger': l.name, 'type': l.ledger_type, 'balance': l.current_balance} for l in ledgers],
        'stock_summary': [{'item': i.name, 'qty': i.quantity, 'value': i.quantity*i.purchase_price} for i in items],
        'sales_register': [v for v in vouchers if v.voucher_type=='Sales'],
        'purchase_register': [v for v in vouchers if v.voucher_type=='Purchase']
    }

@app.get('/invoice/{voucher_id}/pdf')
def invoice_pdf(voucher_id:int, db:Session=Depends(get_db)):
    v=db.query(Voucher).filter(Voucher.id==voucher_id).first()
    if not v: raise HTTPException(404, 'Voucher not found')
    ledger=db.query(Ledger).filter(Ledger.id==v.party_ledger_id).first()
    item=db.query(StockItem).filter(StockItem.id==v.item_id).first()
    buf=BytesIO(); p=canvas.Canvas(buf, pagesize=A4)
    p.setFont('Helvetica-Bold', 18); p.drawString(50,800,'SmartERP Invoice')
    p.setFont('Helvetica', 11); p.drawString(50,770,f'Voucher No: {v.voucher_no}')
    p.drawString(50,750,f'Date: {v.created_at.strftime("%d-%m-%Y")}')
    p.drawString(50,730,f'Party: {ledger.name if ledger else ""}')
    p.drawString(50,700,f'Item: {item.name if item else ""}')
    p.drawString(50,680,f'Qty: {v.quantity} Rate: {v.rate}')
    p.drawString(50,660,f'Amount: {v.amount}')
    p.drawString(50,640,f'Tax: {v.tax}')
    p.setFont('Helvetica-Bold', 13); p.drawString(50,615,f'Total: {v.total}')
    p.showPage(); p.save(); buf.seek(0)
    return StreamingResponse(buf, media_type='application/pdf', headers={'Content-Disposition':'attachment; filename=invoice.pdf'})

@app.get('/export/{company_id}/excel')
def export_excel(company_id:int, db:Session=Depends(get_db)):
    wb=openpyxl.Workbook(); ws=wb.active; ws.title='Stock Summary'; ws.append(['Item','SKU','Qty','Purchase Price','Value'])
    for i in db.query(StockItem).filter(StockItem.company_id==company_id).all(): ws.append([i.name,i.sku,i.quantity,i.purchase_price,i.quantity*i.purchase_price])
    buf=BytesIO(); wb.save(buf); buf.seek(0)
    return StreamingResponse(buf, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={'Content-Disposition':'attachment; filename=smarterp_report.xlsx'})
