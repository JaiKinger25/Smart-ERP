# SmartERP Clean MVP

This is a simple but complete SmartERP MVP following the required guideline:

- User Register and Login
- JWT-like token authentication
- Company Registration and Selection
- Gateway of SmartERP Dashboard
- Customer/Supplier/Expense/Income/Bank/Cash Ledgers
- Item / Stock Master
- Sales Voucher / Customer Bill
- Purchase Voucher / Indirect Stock Entry
- Automatic stock update
- Ledger balance update
- Reports: Trial Balance, Stock Summary, Sales Register, Purchase Register
- PDF Invoice generation using ReportLab
- Excel export using OpenPyXL
- Keyboard shortcuts

## Demo Login
Email: admin@smarterp.com
Password: admin123

## Start Backend
Open CMD:

cd backend
start_backend.bat

Backend runs on:
http://127.0.0.1:8000

Swagger:
http://127.0.0.1:8000/docs

## Start Frontend
Open second CMD:

cd frontend
start_frontend.bat

Frontend usually runs on:
http://localhost:5173

## Keyboard Shortcuts
F1 = Company Selection
Ctrl + H = Dashboard
Alt + L = Ledgers
Alt + S = Stock Items
F8 = Sales Voucher
F9 = Purchase Voucher
Ctrl + R = Reports
Ctrl + Q = Logout

## Important
This project uses SQLite for easy college/internship demo setup. PostgreSQL can be added later.
