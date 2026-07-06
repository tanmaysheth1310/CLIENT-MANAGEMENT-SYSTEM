import sqlite3

conn = sqlite3.connect("crm.db")
cur = conn.cursor()

with open("schema.sql") as f:
    cur.executescript(f.read())

cur.execute("INSERT INTO admin (username, password) VALUES ('admin', 'admin123')")

clients = [
    ("Rajesh Sharma", "Sharma Textiles", "rajesh@sharmatextiles.in", "9821034567", "Mumbai", "2026-01-12"),
    ("Priya Mehta", "Mehta & Sons Traders", "priya@mehtasons.com", "9876501234", "Ahmedabad", "2026-01-28"),
    ("Arun Iyer", "Iyer Software Solutions", "arun@iyersoft.in", "9945012378", "Chennai", "2026-02-05"),
    ("Sunita Agarwal", "Agarwal Sweets Pvt Ltd", "sunita@agarwalsweets.com", "9812345670", "Jaipur", "2026-02-19"),
    ("Vikram Singh", "Singh Logistics", "vikram@singhlogistics.in", "9990123456", "Delhi", "2026-03-03"),
    ("Deepa Nair", "Nair Ayurveda Kendra", "deepa@nairayurveda.com", "9847012345", "Kochi", "2026-03-15"),
    ("Mohammed Khan", "Khan Builders", "mkhan@khanbuilders.in", "9865432109", "Hyderabad", "2026-03-27"),
    ("Ananya Banerjee", "Banerjee Tea Estate", "ananya@banerjeetea.com", "9830123456", "Kolkata", "2026-04-08"),
    ("Suresh Patil", "Patil Agro Farms", "suresh@patilagro.in", "9822098765", "Pune", "2026-04-21"),
    ("Kavita Reddy", "Reddy Diagnostics", "kavita@reddylabs.com", "9701234567", "Hyderabad", "2026-05-06"),
    ("Harpreet Gill", "Gill Transport Co", "harpreet@gilltransport.in", "9781023456", "Ludhiana", "2026-05-24"),
    ("Nikhil Joshi", "Joshi Book Depot", "nikhil@joshibooks.com", "9420135678", "Nagpur", "2026-06-10"),
]

cur.executemany("INSERT INTO clients (name, company, email, phone, city, created_at) VALUES (?,?,?,?,?,?)", clients)

projects = [
    (1, "Inventory Management System", "Completed", "2026-01-15", "2026-03-10"),
    (2, "Billing Software Upgrade", "Ongoing", "2026-02-01", ""),
    (3, "Company Website Redesign", "Completed", "2026-02-10", "2026-04-05"),
    (4, "Online Order Portal", "Ongoing", "2026-03-01", ""),
    (5, "Fleet Tracking Dashboard", "Ongoing", "2026-03-10", ""),
    (6, "Appointment Booking App", "Completed", "2026-03-20", "2026-05-25"),
    (7, "Site Progress Reports Tool", "Ongoing", "2026-04-01", ""),
    (8, "Tea Export Catalogue Site", "Completed", "2026-04-12", "2026-06-01"),
    (9, "Mandi Price Tracker", "Ongoing", "2026-05-01", ""),
    (10, "Lab Report Portal", "Ongoing", "2026-05-15", ""),
]

cur.executemany("INSERT INTO projects (client_id, title, status, start_date, end_date) VALUES (?,?,?,?,?)", projects)

invoices = [
    (1, 45000, "Paid", "2026-03-12"),
    (2, 30000, "Unpaid", "2026-04-01"),
    (3, 62000, "Paid", "2026-04-08"),
    (4, 25000, "Unpaid", "2026-04-20"),
    (5, 80000, "Paid", "2026-05-02"),
    (6, 38000, "Paid", "2026-05-28"),
    (7, 55000, "Unpaid", "2026-06-05"),
    (8, 47000, "Paid", "2026-06-10"),
    (9, 18000, "Unpaid", "2026-06-18"),
    (10, 33000, "Unpaid", "2026-06-25"),
]

cur.executemany("INSERT INTO invoices (project_id, amount, status, invoice_date) VALUES (?,?,?,?)", invoices)

conn.commit()
conn.close()
print("Database seeded, login with admin / admin123")
