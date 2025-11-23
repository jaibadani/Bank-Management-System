import sqlite3
import random
import smtplib
import threading
import sys
import os
from email.mime.text import MIMEText
from datetime import datetime

# Try importing sound library
try:
    import winsound
    SOUND_ENABLED = True
except ImportError:
    SOUND_ENABLED = False

# --- CONFIGURATION ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "badanij2@gmail.com" 
SENDER_PASSWORD = "sbia ansh ppfb juli" 
MANAGER_EMAIL = "jaibadani28@gmail.com" 
# --- UTILS ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("\nPress Enter to continue...")

def print_header(text):
    clear_screen()
    print("="*50)
    print(f"  {text}")
    print("="*50)
    print()

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    # 1. Accounts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            account_number INTEGER PRIMARY KEY, name TEXT NOT NULL, pin TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE, phone TEXT NOT NULL UNIQUE,
            balance REAL DEFAULT 0.0, acc_type TEXT NOT NULL
        )
    ''')
    # 2. Transactions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, account_number INTEGER, type TEXT,
            amount REAL, timestamp TEXT, FOREIGN KEY(account_number) REFERENCES accounts(account_number)
        )
    ''')
    # 3. Beneficiaries
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS beneficiaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT, owner_acc INTEGER, name TEXT,
            ben_acc_num INTEGER, FOREIGN KEY(owner_acc) REFERENCES accounts(account_number)
        )
    ''')
    # 4. Loans
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT, account_number INTEGER, applicant_name TEXT,
            amount REAL, purpose TEXT, status TEXT DEFAULT 'Pending', request_date TEXT,
            FOREIGN KEY(account_number) REFERENCES accounts(account_number)
        )
    ''')
    # 5. Helpdesk
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS helpdesk (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT, account_number INTEGER, applicant_name TEXT,
            query_text TEXT, status TEXT DEFAULT 'Pending', resolution_text TEXT,
            request_date TEXT, FOREIGN KEY(account_number) REFERENCES accounts(account_number)
        )
    ''')
    
    # Special Accounts
    try:
        cursor.execute("INSERT OR IGNORE INTO accounts VALUES (1, 'Administrator', '0000', 'admin@bank.com', '0000000000', 0.0, 'Admin')")
        cursor.execute("INSERT OR IGNORE INTO accounts VALUES (2, 'Support Team', '0000', 'support@bank.com', '0000000001', 0.0, 'Support')")
    except Exception as e:
        print(f"Error creating special accounts: {e}")
        
    conn.commit()
    conn.close()

# --- EMAIL SYSTEM ---
def send_email_thread(target_email, subject, body):
    try:
        msg = MIMEText(body); msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL; msg['To'] = target_email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls(); server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, target_email, msg.as_string())
        server.quit()
    except Exception as e: 
        pass 

def trigger_email(target_email, subject, body):
    threading.Thread(target=send_email_thread, args=(target_email, subject, body)).start()

# --- SOUND ---
def play_kaching():
    if SOUND_ENABLED:
        try:
            winsound.Beep(1000, 100); winsound.Beep(2000, 300)
        except: pass

# --- CLI APP LOGIC ---
class BankCLI:
    def __init__(self):
        self.current_account = None
        self.user_name = None
        self.user_email = None

    def start(self):
        while True:
            print_header("PYTHON BANK CLI - WELCOME")
            print("1. Login")
            print("2. Create New Account")
            print("3. Forgot ID/PIN")
            print("4. Delete Account")
            print("5. Exit")
            
            choice = input("\nSelect Option: ")
            
            if choice == '1': self.login()
            elif choice == '2': self.create_account()
            elif choice == '3': self.forgot_details()
            elif choice == '4': self.delete_account_flow()
            elif choice == '5': sys.exit()
            else: print("Invalid option."); pause()

    # --- AUTHENTICATION ---
    def login(self):
        print_header("LOGIN")
        try:
            acc = int(input("Account Number: "))
            pin = input("PIN Code: ")
        except ValueError:
            print("Invalid input format."); pause(); return

        conn = sqlite3.connect("bank.db"); cur = conn.cursor()
        cur.execute("SELECT name, email FROM accounts WHERE account_number=? AND pin=?", (acc, pin))
        user = cur.fetchone(); conn.close()
        
        if user:
            self.current_account = acc; self.user_name = user[0]; self.user_email = user[1]
            trigger_email(self.user_email, "Login Alert", f"Login detected at {datetime.now()}")
            
            if acc == 1: self.admin_dashboard()
            elif acc == 2: self.support_dashboard()
            else: self.user_dashboard()
        else:
            print("Invalid Credentials."); pause()

    def perform_otp_check(self, email, action_name, extra=""):
        print(f"\nSending OTP to {email}...")
        otp_code = str(random.randint(1000, 9999))
        trigger_email(email, f"{action_name} Verification", f"{extra}\nOTP: {otp_code}")
        
        user_input = input("Enter the 4-digit OTP received: ")
        if user_input == otp_code: return True
        else: print("❌ Invalid OTP."); return False

    def create_account(self):
        print_header("REGISTER NEW ACCOUNT")
        name = input("Full Name: ")
        email = input("Email: ")
        phone = input("Phone (10 digits): ")
        
        conn = sqlite3.connect("bank.db"); cur = conn.cursor()
        cur.execute("SELECT * FROM accounts WHERE email=? OR phone=?", (email, phone))
        if cur.fetchone():
            print("Error: Email or Phone already registered."); conn.close(); pause(); return
        if len(phone) != 10 or not phone.isdigit():
            print("Error: Phone must be 10 digits."); conn.close(); pause(); return
        conn.close()

        pin = input("Set PIN: ")
        atype = input("Account Type (Savings/Current): ")
        
        if self.perform_otp_check(email, "Account Creation"):
            acc_num = random.randint(100000, 999999)
            conn = sqlite3.connect("bank.db"); cur = conn.cursor()
            cur.execute("INSERT INTO accounts VALUES (?, ?, ?, ?, ?, ?, ?)", (acc_num, name, pin, email, phone, 0.0, atype))
            conn.commit(); conn.close()
            trigger_email(email, "Welcome", f"Your Account Number is: {acc_num}")
            print(f"\n✅ Success! Your Account Number is: {acc_num}"); pause()
        else:
            pause()

    def forgot_details(self):
        print_header("RECOVER ACCOUNT")
        email = input("Enter Registered Email: ")
        conn = sqlite3.connect("bank.db"); cur = conn.cursor()
        cur.execute("SELECT name, account_number, pin FROM accounts WHERE email=?", (email,))
        u = cur.fetchone(); conn.close()
        if u:
            trigger_email(email, "Account Recovery", f"Hello {u[0]},\nID: {u[1]}\nPIN: {u[2]}")
            print("✅ Recovery details sent to your email."); pause()
        else:
            print("❌ Email not found."); pause()

    def delete_account_flow(self):
        print_header("DELETE ACCOUNT")
        try:
            acc = int(input("Account Num: "))
            pin = input("PIN: ")
        except: return

        conn = sqlite3.connect("bank.db"); cur = conn.cursor()
        cur.execute("SELECT email FROM accounts WHERE account_number=? AND pin=?", (acc, pin))
        user = cur.fetchone(); conn.close()
        
        if user and self.perform_otp_check(user[0], "DELETE ACCOUNT"):
            self.perform_deletion(acc)
            print("Account deleted successfully."); pause()
        else:
            print("Invalid credentials or OTP failed."); pause()

    def perform_deletion(self, acc):
        conn = sqlite3.connect("bank.db"); cur = conn.cursor()
        cur.execute("DELETE FROM accounts WHERE account_number=?", (acc,))
        cur.execute("DELETE FROM transactions WHERE account_number=?", (acc,))
        cur.execute("DELETE FROM beneficiaries WHERE owner_acc=?", (acc,))
        cur.execute("DELETE FROM beneficiaries WHERE ben_acc_num=?", (acc,))
        cur.execute("DELETE FROM loans WHERE account_number=?", (acc,))
        cur.execute("DELETE FROM helpdesk WHERE account_number=?", (acc,))
        conn.commit(); conn.close()

    # --- ADMIN DASHBOARD ---
    def admin_dashboard(self):
        while True:
            conn = sqlite3.connect("bank.db"); cur = conn.cursor()
            cur.execute("SELECT SUM(balance) FROM accounts WHERE account_number NOT IN (1, 2)")
            liq = cur.fetchone()[0] or 0.0
            cur.execute("SELECT COUNT(*) FROM accounts WHERE account_number NOT IN (1, 2)")
            users = cur.fetchone()[0]; conn.close()

            print_header("ADMINISTRATOR PANEL")
            print(f"Liquidity: ${liq:,.2f}  |  Total Users: {users}")
            print("\n1. Manage Loans (Approve/Decline)")
            print("2. Run Monthly EMI (5%)")
            print("3. List All Users")
            print("4. Force Delete User")
            print("5. Logout")

            choice = input("\nSelect: ")
            if choice == '1': self.admin_loans()
            elif choice == '2': self.admin_emi()
            elif choice == '3': self.admin_users()
            elif choice == '4': self.admin_force_delete()
            elif choice == '5': self.current_account = None; break

    def admin_loans(self):
        print_header("PENDING LOANS")
        conn = sqlite3.connect("bank.db") # Connection opened here
        cur = conn.cursor()
        cur.execute("SELECT loan_id, applicant_name, amount, purpose FROM loans WHERE status='Pending'")
        loans = cur.fetchall()
        
        if not loans: 
            print("No pending loans.")
            conn.close()
            pause()
            return
        
        for l in loans:
            print(f"ID: {l[0]} | {l[1]} | Req: ${l[2]} | Purpose: {l[3]}")
        
        lid = input("\nEnter Loan ID to action (or Enter to back): ")
        if not lid: 
            conn.close()
            return
        
        action = input("Approve (a) or Decline (d)? ").lower()
        if action not in ['a', 'd']: 
            conn.close()
            return

        cur.execute("SELECT account_number, amount FROM loans WHERE loan_id=?", (lid,))
        ld = cur.fetchone()
        if not ld: 
            print("Invalid ID")
            conn.close()
            pause()
            return
        
        acc, amt = ld[0], ld[1]
        cur.execute("SELECT email FROM accounts WHERE account_number=?", (acc,))
        email = cur.fetchone()[0]

        status = "Approved" if action == 'a' else "Declined"
        cur.execute("UPDATE loans SET status=? WHERE loan_id=?", (status, lid))
        
        if action == 'a':
            cur.execute("UPDATE accounts SET balance = balance + ? WHERE account_number=?", (amt, acc))
            # Use existing cursor to log transaction to prevent DB Lock
            cur.execute("INSERT INTO transactions VALUES (NULL, ?, ?, ?, ?)", 
                        (acc, "Loan Approved", amt, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            trigger_email(email, "Loan Approved", f"Your loan of ${amt} is approved.")
            print("Loan Approved.")
        else:
            trigger_email(email, "Loan Declined", f"Your loan of ${amt} was declined.")
            print("Loan Declined.")
            
        conn.commit()
        conn.close()
        pause()

    def admin_emi(self):
        print("Processing 5% EMI deduction for all approved loans...")
        conn = sqlite3.connect("bank.db") # Connection opened here
        cur = conn.cursor()
        cur.execute("SELECT account_number, amount, applicant_name, email FROM loans JOIN accounts ON loans.account_number = accounts.account_number WHERE status='Approved'")
        loans = cur.fetchall()
        
        for l in loans:
            acc, amt, name, email = l; emi = amt * 0.05
            cur.execute("UPDATE accounts SET balance = balance - ? WHERE account_number=?", (emi, acc))
            
            # Use existing cursor to log transaction to prevent DB Lock
            cur.execute("INSERT INTO transactions VALUES (NULL, ?, ?, ?, ?)", 
                        (acc, "Loan EMI", emi, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            trigger_email(email, "Loan Repayment", f"Dear {name},\n\nEMI of ${emi} (5%) deducted.")
            
        conn.commit()
        conn.close()
        print(f"Processed EMI for {len(loans)} loans."); pause()

    def admin_users(self):
        print_header("USER LIST")
        conn = sqlite3.connect("bank.db"); cur = conn.cursor()
        cur.execute("SELECT account_number, name, balance, email FROM accounts WHERE account_number NOT IN (1, 2)")
        for r in cur.fetchall():
            print(f"{r[0]} | {r[1]:<15} | ${r[2]:<10,.2f} | {r[3]}")
        conn.close(); pause()

    def admin_force_delete(self):
        acc = input("Enter Account ID to force delete: ")
        confirm = input("Are you sure? (yes/no): ")
        if confirm.lower() == "yes":
            self.perform_deletion(acc)
        pause()

    # --- SUPPORT DASHBOARD ---
    def support_dashboard(self):
        while True:
            print_header("HELP DESK PORTAL")
            print("1. View Pending Queries")
            print("2. Resolve Query")
            print("3. View Resolved History")
            print("4. Logout")
            
            choice = input("\nSelect: ")
            if choice == '1': self.support_view_pending()
            elif choice == '2': self.support_resolve()
            elif choice == '3': self.support_history()
            elif choice == '4': self.current_account = None; break

    def support_view_pending(self):
        print_header("PENDING TICKETS")
        conn = sqlite3.connect("bank.db"); cur = conn.cursor()
        cur.execute("SELECT ticket_id, request_date, applicant_name, query_text FROM helpdesk WHERE status='Pending'")
        rows = cur.fetchall(); conn.close()
        for r in rows:
            print(f"ID: {r[0]} | {r[1]} | From: {r[2]}")
            print(f"Query: {r[3]}")
            print("-" * 40)
        pause()

    def support_resolve(self):
        tid = input("Enter Ticket ID to resolve: ")
        conn = sqlite3.connect("bank.db"); cur = conn.cursor()
        cur.execute("SELECT applicant_name, account_number, query_text FROM helpdesk WHERE ticket_id=? AND status='Pending'", (tid,))
        data = cur.fetchone()
        
        if not data: print("Ticket not found or already resolved."); conn.close(); pause(); return
        
        print(f"\nUser: {data[0]} | Query: {data[2]}")
        res = input("Enter Resolution: ")
        
        cur.execute("UPDATE helpdesk SET status='Resolved', resolution_text=? WHERE ticket_id=?", (res, tid))
        conn.commit()
        
        cur.execute("SELECT email FROM accounts WHERE account_number=?", (data[1],))
        u_email = cur.fetchone()[0]
        conn.close()
        
        trigger_email(u_email, f"Reply for Ticket #{tid}", f"Query: {data[2]}\n\nResponse: {res}")
        print("Resolution sent."); pause()

    def support_history(self):
        print_header("RESOLVED HISTORY")
        conn = sqlite3.connect("bank.db"); cur = conn.cursor()
        cur.execute("SELECT ticket_id, applicant_name, query_text, resolution_text FROM helpdesk WHERE status='Resolved' ORDER BY ticket_id DESC LIMIT 10")
        for r in cur.fetchall():
            print(f"ID: {r[0]} | User: {r[1]}")
            print(f"Q: {r[2]}\nA: {r[3]}\n")
        conn.close(); pause()

    # --- USER DASHBOARD ---
    def user_dashboard(self):
        while True:
            conn = sqlite3.connect("bank.db"); cur = conn.cursor()
            cur.execute("SELECT balance, acc_type FROM accounts WHERE account_number=?", (self.current_account,))
            res = cur.fetchone(); conn.close()
            bal, atype = res if res else (0, "N/A")

            print_header(f"Welcome, {self.user_name}")
            print(f"Account Type: {atype}")
            print(f"Balance:      ${bal:,.2f}")
            print("-" * 30)
            print("1. Deposit Money")
            print("2. Withdraw Money")
            print("3. Transfer Funds")
            print("4. View Statement")
            print("5. Manage Beneficiaries")
            print("6. Apply for Loan")
            print("7. Check Loan Status")
            print("8. Help Desk")
            print("9. Profile Settings")
            print("0. Logout")

            c = input("\nSelect: ")
            if c == '1': self.deposit()
            elif c == '2': self.withdraw(bal)
            elif c == '3': self.transfer(bal)
            elif c == '4': self.view_statement()
            elif c == '5': self.manage_beneficiaries()
            elif c == '6': self.apply_loan()
            elif c == '7': self.check_loan()
            elif c == '8': self.help_desk()
            elif c == '9': self.profile()
            elif c == '0': self.current_account = None; break

    def deposit(self):
        try: amt = float(input("Enter Amount to Deposit: "))
        except: return
        if amt > 0:
            self.update_balance(amt)
            self.log_trans("Deposit", amt)
            trigger_email(self.user_email, "Deposit Alert", f"Credited: ${amt}")
            play_kaching()
            print("✅ Deposit Successful!")
        pause()

    def withdraw(self, current_bal):
        try: amt = float(input("Enter Amount to Withdraw: "))
        except: return
        if amt > 0 and current_bal >= amt:
            if self.perform_otp_check(self.user_email, "Withdrawal"):
                self.update_balance(-amt)
                self.log_trans("Withdrawal", amt)
                trigger_email(self.user_email, "Withdrawal Alert", f"Debited: ${amt}")
                print("✅ Withdrawal Successful!")
        else:
            print("❌ Insufficient funds or invalid amount.")
        pause()

    def transfer(self, current_bal):
        print("\n--- Transfer ---")
        print("1. Select from Beneficiaries")
        print("2. Enter Account Number Manually")
        c = input("Option: ")
        target_acc = None

        if c == '1':
            conn = sqlite3.connect("bank.db"); cur = conn.cursor()
            cur.execute("SELECT name, ben_acc_num FROM beneficiaries WHERE owner_acc=?", (self.current_account,))
            bens = cur.fetchall(); conn.close()
            if not bens: print("No beneficiaries found."); return
            for i, b in enumerate(bens):
                print(f"{i+1}. {b[0]} ({b[1]})")
            try:
                idx = int(input("Enter number: ")) - 1
                if 0 <= idx < len(bens): target_acc = bens[idx][1]
            except: return
        elif c == '2':
            try: target_acc = int(input("Target Account Num: "))
            except: return
        else: return

        if not target_acc or target_acc == self.current_account: print("Invalid Target."); pause(); return

        conn = sqlite3.connect("bank.db"); cur = conn.cursor()
        cur.execute("SELECT name, email FROM accounts WHERE account_number=?", (target_acc,))
        rec = cur.fetchone(); conn.close()
        
        if not rec: print("Account not found."); pause(); return
        
        print(f"Transferring to: {rec[0]}")
        try: amt = float(input("Amount: "))
        except: return
        
        if amt > 0 and current_bal >= amt:
            if self.perform_otp_check(self.user_email, "Transfer", f"To: {rec[0]} (${amt})"):
                self.update_balance(-amt)
                self.update_balance_target(target_acc, amt)
                self.log_trans("Transfer Sent", amt)
                self.log_trans_target(target_acc, "Transfer Received", amt)
                
                trigger_email(self.user_email, "Debit Alert", f"Sent ${amt} to {rec[0]}")
                trigger_email(rec[1], "Credit Alert", f"Received ${amt} from {self.user_name}")
                print("✅ Transfer Successful!")
        else:
            print("❌ Insufficient funds.")
        pause()

    def view_statement(self):
        print_header("MINI STATEMENT")
        print("Filter: 1. All | 2. Deposit | 3. Withdrawal | 4. Transfer")
        f = input("Select Filter (1-4): ")
        f_map = {'1': 'All', '2': 'Deposit', '3': 'Withdraw', '4': 'Transfer'}
        ft = f_map.get(f, "All")
        
        conn = sqlite3.connect("bank.db"); cur = conn.cursor()
        q = "SELECT timestamp, type, amount FROM transactions WHERE account_number=? "
        p = [self.current_account]
        if ft != "All": 
            q += "AND type LIKE ? "
            p.append(f"%{ft}%")
        q += "ORDER BY id DESC LIMIT 20"
        
        cur.execute(q, p)
        rows = cur.fetchall(); conn.close()
        
        print(f"{'Date':<20} | {'Type':<20} | {'Amount':<10}")
        print("-" * 60)
        for r in rows:
            print(f"{r[0]:<20} | {r[1]:<20} | ${r[2]:<10,.2f}")
        pause()

    def manage_beneficiaries(self):
        print_header("BENEFICIARIES")
        conn = sqlite3.connect("bank.db"); cur = conn.cursor()
        cur.execute("SELECT name, ben_acc_num FROM beneficiaries WHERE owner_acc=?", (self.current_account,))
        for r in cur.fetchall(): print(f"- {r[0]} ({r[1]})")
        
        print("\n1. Add New | 0. Back")
        if input("Choice: ") == '1':
            try: b_acc = int(input("Beneficiary Acc Num: "))
            except: conn.close(); return
            
            cur.execute("SELECT name FROM accounts WHERE account_number=?", (b_acc,))
            res = cur.fetchone()
            if res and b_acc != self.current_account:
                cur.execute("INSERT INTO beneficiaries VALUES (NULL, ?, ?, ?)", (self.current_account, res[0], b_acc))
                conn.commit()
                print("✅ Added!")
            else:
                print("❌ Account not found or invalid.")
        conn.close(); pause()

    def apply_loan(self):
        print_header("LOAN APPLICATION")
        try: amt = float(input("Amount: "))
        except: return
        reason = input("Purpose (min 5 words): ")
        
        if len(reason.split()) < 5: print("Purpose too short."); pause(); return
        
        conn = sqlite3.connect("bank.db"); cur = conn.cursor()
        cur.execute("INSERT INTO loans (account_number, applicant_name, amount, purpose, status, request_date) VALUES (?, ?, ?, ?, ?, ?)",
                    (self.current_account, self.user_name, amt, reason, 'Pending', datetime.now().strftime("%Y-%m-%d")))
        conn.commit(); conn.close()
        trigger_email(MANAGER_EMAIL, "Loan Request", f"User: {self.user_name}\nAmt: ${amt}\nPurpose: {reason}")
        print("✅ Application Submitted."); pause()

    def check_loan(self):
        print_header("LOAN STATUS")
        conn = sqlite3.connect("bank.db"); cur = conn.cursor()
        cur.execute("SELECT request_date, amount, status FROM loans WHERE account_number=? ORDER BY loan_id DESC", (self.current_account,))
        print(f"{'Date':<12} | {'Amount':<10} | {'Status'}")
        for r in cur.fetchall():
            print(f"{r[0]:<12} | ${r[1]:<9} | {r[2]}")
        conn.close(); pause()

    def help_desk(self):
        while True:
            print_header("HELP DESK")
            print("1. Submit New Ticket")
            print("2. View My Tickets")
            print("3. Back")
            c = input("Choice: ")
            
            if c == '1':
                q = input("Type your query: ")
                if len(q) < 5: print("Too short."); continue
                conn = sqlite3.connect("bank.db"); cur = conn.cursor()
                cur.execute("INSERT INTO helpdesk (account_number, applicant_name, query_text, request_date) VALUES (?, ?, ?, ?)",
                            (self.current_account, self.user_name, q, datetime.now().strftime("%Y-%m-%d")))
                conn.commit(); conn.close()
                trigger_email(MANAGER_EMAIL, "New Help Ticket", f"From: {self.user_name}\nQuery: {q}")
                print("✅ Ticket Submitted!")
                
            elif c == '2':
                conn = sqlite3.connect("bank.db"); cur = conn.cursor()
                cur.execute("SELECT request_date, status, query_text, resolution_text FROM helpdesk WHERE account_number=? ORDER BY ticket_id DESC", (self.current_account,))
                for r in cur.fetchall():
                    print(f"\nDate: {r[0]} | Status: {r[1]}")
                    print(f"Q: {r[2]}")
                    if r[3]: print(f"A: {r[3]}")
                    print("-" * 30)
                conn.close(); pause()
            elif c == '3': break

    def profile(self):
        print_header("PROFILE")
        conn = sqlite3.connect("bank.db"); cur = conn.cursor()
        cur.execute("SELECT name, email, phone FROM accounts WHERE account_number=?", (self.current_account,))
        d = cur.fetchone(); conn.close()
        print(f"Name:  {d[0]}")
        print(f"Email: {d[1]}")
        print(f"Phone: {d[2]}")
        print("\nUpdate: 1. Email | 2. Phone | 3. PIN | 0. Back")
        
        c = input("Select: ")
        field_map = {'1': 'email', '2': 'phone', '3': 'pin'}
        if c in field_map:
            new_val = input(f"Enter new {field_map[c]}: ")
            if self.perform_otp_check(self.user_email, "Update Profile"):
                conn = sqlite3.connect("bank.db"); cur = conn.cursor()
                try:
                    cur.execute(f"UPDATE accounts SET {field_map[c]}=? WHERE account_number=?", (new_val, self.current_account))
                    conn.commit()
                    print("Updated!"); 
                    if c == '1': self.user_email = new_val
                except: print("Error: Value may already exist.")
                conn.close(); pause()

    # --- DB HELPERS (For user operations) ---
    def update_balance(self, amt):
        conn = sqlite3.connect("bank.db"); cur = conn.cursor()
        cur.execute("UPDATE accounts SET balance = balance + ? WHERE account_number=?", (amt, self.current_account))
        conn.commit(); conn.close()

    def update_balance_target(self, acc, amt):
        conn = sqlite3.connect("bank.db"); cur = conn.cursor()
        cur.execute("UPDATE accounts SET balance = balance + ? WHERE account_number=?", (amt, acc))
        conn.commit(); conn.close()

    def log_trans(self, t, amt):
        conn = sqlite3.connect("bank.db"); cur = conn.cursor()
        cur.execute("INSERT INTO transactions VALUES (NULL, ?, ?, ?, ?)", (self.current_account, t, amt, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit(); conn.close()

    def log_trans_target(self, acc, t, amt):
        conn = sqlite3.connect("bank.db"); cur = conn.cursor()
        cur.execute("INSERT INTO transactions VALUES (NULL, ?, ?, ?, ?)", (acc, t, amt, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit(); conn.close()

# --- ENTRY POINT ---
if __name__ == "__main__":
    init_db()
    app = BankCLI()
    try:
        app.start()
    except KeyboardInterrupt:
        print("\nGoodbye!")