import sqlite3

def mk_db():
    db = sqlite3.connect("bank.db")
    c = db.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            account_number INTEGER PRIMARY KEY, name TEXT NOT NULL, pin TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE, phone TEXT NOT NULL UNIQUE,
            balance REAL DEFAULT 0.0, acc_type TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, account_number INTEGER, type TEXT,
            amount REAL, timestamp TEXT, FOREIGN KEY(account_number) REFERENCES accounts(account_number)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS beneficiaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT, owner_acc INTEGER, name TEXT,
            ben_acc_num INTEGER, FOREIGN KEY(owner_acc) REFERENCES accounts(account_number)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT, account_number INTEGER, applicant_name TEXT,
            amount REAL, purpose TEXT, status TEXT DEFAULT 'Pending', request_date TEXT,
            FOREIGN KEY(account_number) REFERENCES accounts(account_number)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS helpdesk (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT, account_number INTEGER, applicant_name TEXT,
            query_text TEXT, status TEXT DEFAULT 'Pending', resolution_text TEXT,
            request_date TEXT, FOREIGN KEY(account_number) REFERENCES accounts(account_number)
        )
    ''')
    c.execute("INSERT OR IGNORE INTO accounts VALUES (1, 'Administrator', '0000', 'jaibadani28@gmail.com', '0000000000', 0.0, 'Admin')")
    c.execute("INSERT OR IGNORE INTO accounts VALUES (2, 'Support Team', '0000', 'jaibadani28@gmail.com', '0000000001', 0.0, 'Support')")
    db.commit()
    db.close()