import sqlite3
import random
import sys
from datetime import datetime
import config
from utils import nice_head, wait_a_bit, send_mail, play_cash,send_mail_multi, generate_statement_pdf,send_mail_pdf
import threading

class Bank:
    def __init__(self):
        self.logged_acc = None
        self.whoami = None
        self.user_mail = None

    def start(self):
        while True:
            nice_head("CiaoBank — welcome peep")
            print("1. Log in")
            print("2. Open new acct")
            print("3. Recover ID / PIN")
            print("4. Remove acct")
            print("5. Exit")
            choice = input("\nChoos an option: ").strip()
            if choice == '1':
                self.do_login()
            elif choice == '2':
                self.new_account()
            elif choice == '3':
                self.recover()
            elif choice == '4':
                self.remove_flow()
            elif choice == '5':
                sys.exit()
            else:
                print("nahh, pick correct option.")
                wait_a_bit()

    def do_login(self):
        nice_head("Login")
        try:
            acct = int(input("Account number: ").strip())
            pin = input("Enter you PIN: ").strip()
        except ValueError:
            print("Please enter good account number.")
            wait_a_bit()
            return
        if (acct == 3):
            self.alerter_screen()
            return
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        
        c.execute("SELECT name, email FROM accounts WHERE account_number=? AND pin=?", (acct, pin))
        u = c.fetchone()
        db.close()
        if u:
            self.logged_acc = acct
            self.whoami = u[0]
            self.user_mail = u[1]
            if (acct != 1 and acct != 2):
                send_mail(self.user_mail, "Login notice", f"Hello {self.whoami},\n\nWe have noticed a login at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. If not you, tell us.")
            if acct == 1:
                self.admin_screen()
            elif acct == 2:
                self.support_screen()
            elif acct == 3:
                self.alerter_screen()
            else:
                self.user_screen()
        else:
            print("Wrong details. Check your number and PIN.")
            wait_a_bit()
    def alerter_screen(self):
        nice_head("ALERTER SCREEN")
        msg = input("Type your alert message to all users: ").strip()
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("SELECT email FROM accounts WHERE account_number NOT IN (1, 2)")
        rows = c.fetchall()
        for x in range(len(rows)):
            rows[x] = rows[x][0]
        db.close()
        print(rows)
        send_mail_multi(list(rows), "CiaoBank Alert", f"Hello user,\n\n{msg}\nThanking you,\nCiaoBank Team")
    def send_otp(self, mailaddr, thing, extra=""):
        print(f"\nSending one-time code to {mailaddr}...")
        code = str(random.randint(1000, 9999))
        send_mail(mailaddr, f"{thing} code", f"{extra}\nCode: {code}")
        got = input("Type the 4-digit code u got: ").strip()
        if got == code:
            return True
        else:
            print("wrong code bud.")
            return False

    def new_account(self):
        nice_head("Open a New Account")
        name = input("Full name: ").strip()
        if (name == ""):
            print("Name cannot be empty.")
            wait_a_bit()
            return
        mail = input("Email: ").strip()
        phone = input("Phone (10 digits): ").strip()
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("SELECT * FROM accounts WHERE email=? OR phone=?", (mail, phone))
        if c.fetchone():
            print("Email or phone already in our messy list.")
            db.close()
            wait_a_bit()
            return
        if len(phone) != 10 or not phone.isdigit():
            print("Phone must be 10 digits mate.")
            db.close()
            wait_a_bit()
            return
        pin = input("Pick a PIN: ").strip()
        at = input("Account type (Savings/Current): ").strip()
        if self.send_otp(mail, "Account creation"):
            acctno = random.randint(100000, 999999)
            c.execute("INSERT INTO accounts VALUES (?, ?, ?, ?, ?, ?, ?)", (acctno, name, pin, mail, phone, 0.0, at))
            db.commit()
            db.close()
            send_mail(mail, "Welcome to CiaoBank", f"Hi {name},\n\nYour acct number is: {acctno}")
            print(f"Done — your acct number: {acctno}. Keep it safe.")
            wait_a_bit()
        else:
            db.close()
            wait_a_bit()

    def recover(self):
        nice_head("Recover Account")
        mail = input("Registered email: ").strip()
        if '@' not in mail or '.' not in mail:
            print("Enter a valid email.")
            wait_a_bit()
            return
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("SELECT name, account_number, pin FROM accounts WHERE email=?", (mail,))
        r = c.fetchone()
        db.close()
        if r:
            send_mail(mail, "Account recovery", f"Hello {r[0]},\n\nAccount ID: {r[1]}\nPIN: {r[2]}")
            print("Recovery details sent. Check your mail.")
            wait_a_bit()
        else:
            print("No account linked to that email.")
            wait_a_bit()

    def remove_flow(self):
        nice_head("Delete Account")
        try:
            acct = int(input("Account number: ").strip())
            pin = input("Your PIN: ").strip()
        except Exception:
            return
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("SELECT email FROM accounts WHERE account_number=? AND pin=?", (acct, pin))
        r = c.fetchone()
        db.close()
        if r and self.send_otp(r[0], "Account deletion"):
            self.wipe(acct)
            print("Account and stuffs removed.")
            wait_a_bit()
        else:
            print("Either wrong creds or code failed.")
            wait_a_bit()

    def wipe(self, acct):
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("DELETE FROM accounts WHERE account_number=?", (acct,))
        c.execute("DELETE FROM transactions WHERE account_number=?", (acct,))
        c.execute("DELETE FROM beneficiaries WHERE owner_acc=?", (acct,))
        c.execute("DELETE FROM beneficiaries WHERE ben_acc_num=?", (acct,))
        # c.execute("DELETE FROM loans WHERE account_number=?", (acct,))
        # c.execute("DELETE FROM helpdesk WHERE account_number=?", (acct,))
        db.commit()
        db.close()

    def admin_screen(self):
        while True:
            db = sqlite3.connect("bank.db")
            c = db.cursor()
            c.execute("SELECT SUM(balance) FROM accounts WHERE account_number NOT IN (1, 2)")
            tot = c.fetchone()[0] or 0.0
            c.execute("SELECT COUNT(*) FROM accounts WHERE account_number NOT IN (1, 2)")
            usr = c.fetchone()[0]
            db.close()
            nice_head("Admin panel")
            print(f"Total cash: ₹{tot:,.2f}  |  Users: {usr}")
            print("\n1. Manage loans")
            print("2. List users")
            print("3. Force delete user")
            print("4. Logout")
            ch = input("\nChoose: ").strip()
            if ch == '1':
                self.admin_loans()
            elif ch == '2':
                self.list_users()
            elif ch == '3':
                self.force_del()
            elif ch == '4':
                self.logged_acc = None
                break

    def admin_loans(self):
        nice_head("Loan requests")
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("SELECT loan_id, applicant_name, amount, purpose FROM loans WHERE status='Pending'")
        rows = c.fetchall()
        if not rows:
            print("No pending loan requests right now.")
            db.close()
            wait_a_bit()
            return
        for r in rows:
            print(f"ID: {r[0]} | {r[1]} | ₹{r[2]} | {r[3]}")
        lid = input("\nEnter loan ID (or Enter to back): ").strip()
        if not lid:
            db.close()
            return
        act = input("Approve (a) or Decline (d)? ").strip().lower()
        if act not in ['a', 'd', 'approve', 'decline', 'y', 'n', '1', '0']:
            db.close()
            return
        if act in ['approve', 'y', '1']:
            act = 'a'
        else:
            act = 'd'
        c.execute("SELECT account_number, amount FROM loans WHERE loan_id=?", (lid,))
        rr = c.fetchone()
        if not rr:
            print("No such loan id.")
            db.close()
            wait_a_bit()
            return
        acct, amt = rr[0], rr[1]
        c.execute("SELECT email FROM accounts WHERE account_number=?", (acct,))
        emr = c.fetchone()
        em = emr[0] if emr else None
        st = "Approved" if act == 'a' else "Declined"
        c.execute("UPDATE loans SET status=? WHERE loan_id=?", (st, lid))
        if act == 'a':
            c.execute("UPDATE accounts SET balance = balance + ? WHERE account_number=?", (amt, acct))
            c.execute("INSERT INTO transactions VALUES (NULL, ?, ?, ?, ?)", (acct, "Loan Approved", amt, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            if em:
                send_mail(em, "Loan approved", f"Congrats — your loan of ₹{amt} is approved.")
            print("Loan approved and money added.")
        else:
            if em:
                send_mail(em, "Loan declined", f"Sorry, your loan for ₹{amt} was declined.")
            print("Loan declined.")
        db.commit()
        db.close()
        wait_a_bit()

    def list_users(self):
        nice_head("Users list")
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("SELECT account_number, name, balance, email FROM accounts WHERE account_number NOT IN (1, 2)")
        for r in c.fetchall():
            print(f"{r[0]} | {r[1]:<15} | ₹{r[2]:<10,.2f} | {r[3]}")
        db.close()
        wait_a_bit()

    def force_del(self):
        nice_head("Users list")
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("SELECT account_number, name, balance, email FROM accounts WHERE account_number NOT IN (1, 2)")
        for r in c.fetchall():
            print(f"{r[0]} | {r[1]:<15} | ₹{r[2]:<10,.2f} | {r[3]}")
        who = input("Account ID to remove: ").strip()
        y = input("Type 'yes' to confirm: ").strip().lower()
        if y == "yes":
            try:
                i = int(who)
                self.wipe(i)
                print("User removed.")
            except Exception:
                print("Could not remove that one.")
        wait_a_bit()

    def support_screen(self):
        while True:
            nice_head("Support desk")
            print("1. View pending tickets")
            print("2. Resolve ticket")
            print("3. View resolved")
            print("4. Logout")
            ch = input("\nPick: ").strip()
            if ch == '1':
                self.view_pending()
            elif ch == '2':
                self.resolve_ticket()
            elif ch == '3':
                self.view_resolved()
            elif ch == '4':
                self.logged_acc = None
                break

    def view_pending(self):
        nice_head("Pending tickets")
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("SELECT ticket_id, request_date, applicant_name, query_text FROM helpdesk WHERE status='Pending'")
        rows = c.fetchall()
        db.close()
        for r in rows:
            print(f"ID: {r[0]} | {r[1]} | From: {r[2]}")
            print(f"Q: {r[3]}")
            print("-" * 40)
        wait_a_bit()

    def resolve_ticket(self):
        nice_head("Pending tickets")
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("SELECT ticket_id, request_date, applicant_name, query_text FROM helpdesk WHERE status='Pending'")
        rows = c.fetchall()
        db.close()
        for r in rows:
            print(f"ID: {r[0]} | {r[1]} | From: {r[2]}")
            print(f"Q: {r[3]}")
            print("-" * 40)
        tid = input("Ticket ID to resolve: ").strip()
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("SELECT applicant_name, account_number, query_text FROM helpdesk WHERE ticket_id=? AND status='Pending'", (tid,))
        d = c.fetchone()
        if not d:
            print("Ticket missing or already done.")
            db.close()
            wait_a_bit()
            return
        print(f"\nFrom: {d[0]} | Q: {d[2]}")
        ans = input("Your resolution: ").strip()
        c.execute("UPDATE helpdesk SET status='Resolved', resolution_text=? WHERE ticket_id=?", (ans, tid))
        c.execute("SELECT email FROM accounts WHERE account_number=?", (d[1],))
        emr = c.fetchone()
        em = emr[0] if emr else None
        db.commit()
        db.close()
        if em:
            send_mail(em, f"Reply ticket #{tid}", f"Q: {d[2]}\n\nA: {ans}")
        print("User replied.")
        wait_a_bit()

    def view_resolved(self):
        nice_head("Resolved tickets")
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("SELECT ticket_id, applicant_name, query_text, resolution_text FROM helpdesk WHERE status='Resolved' ORDER BY ticket_id DESC LIMIT 10")
        for r in c.fetchall():
            print(f"ID: {r[0]} | User: {r[1]}")
            print(f"Q: {r[2]}\nA: {r[3]}\n")
        db.close()
        wait_a_bit()

    def user_screen(self):
        while True:
            db = sqlite3.connect("bank.db")
            c = db.cursor()
            c.execute("SELECT balance, acc_type FROM accounts WHERE account_number=?", (self.logged_acc,))
            res = c.fetchone()
            db.close()
            bal, at = res if res else (0, "N/A")
            nice_head(f"Hey, {self.whoami}")
            print(f"Type: {at}")
            print(f"Balance: ₹{bal:,.2f}")
            print("-" * 30)
            print("1. Deposit")
            print("2. Withdraw")
            print("3. Send money")
            print("4. Statement")
            print("5. Beneficiaries")
            print("6. Apply loan")
            print("7. Loan status")
            print("8. Help desk")
            print("9. Profile")
            print("0. Logout")
            ch = input("\nPick: ").strip()
            if ch == '1':
                self.deposit()
            elif ch == '2':
                self.withdraw(bal)
            elif ch == '3':
                self.transfer(bal)
            elif ch == '4':
                self.statement()
            elif ch == '5':
                self.bens()
            elif ch == '6':
                self.apply_loan()
            elif ch == '7':
                self.check_loan()
            elif ch == '8':
                self.helpdesk()
            elif ch == '9':
                self.profile()
            elif ch == '0':
                self.logged_acc = None
                break

    def deposit(self):
        try:
            amount = float(input("How much deposit? ").strip())
        except Exception:
            return
        if amount > 0:
            self.bump_bal(amount)
            self.log_it("Deposit", amount)
            send_mail(self.user_mail, "Deposit notif", f"₹{amount} credited to your acct.")
            # play_cash()
            print("Deposit done, cheers!")
            play_cash()
        wait_a_bit()

    def withdraw(self, curbal):
        try:
            amount = float(input("Amount to withdraw: ").strip())
        except Exception:
            return
        if amount > 0 and curbal >= amount:
            if self.send_otp(self.user_mail, "Withdrawal"):
                self.bump_bal(-amount)
                self.log_it("Withdrawal", amount)
                send_mail(self.user_mail, "Withdrawal alert", f"₹{amount} debited.")
                print("Take your cash.")
        else:
            print("Not enough money or bad amount.")
        wait_a_bit()

    def transfer(self, curbal):
        print("\nTransfer money")
        print("1. From my beneficiaries")
        print("2. Enter acct number")
        pick = input("Choice: ").strip()
        tgt = None
        if pick == '1':
            db = sqlite3.connect("bank.db")
            c = db.cursor()
            c.execute("SELECT name, ben_acc_num FROM beneficiaries WHERE owner_acc=?", (self.logged_acc,))
            rows = c.fetchall()
            db.close()
            if not rows:
                print("No beneficiaries yet.")
                wait_a_bit()
                return
            for i, r in enumerate(rows):
                print(f"{i+1}. {r[0]} ({r[1]})")
            try:
                idx = int(input("Select number: ").strip()) - 1
                if 0 <= idx < len(rows):
                    tgt = rows[idx][1]
            except Exception:
                return
        elif pick == '2':
            try:
                tgt = int(input("Target acct: ").strip())
            except Exception:
                return
        else:
            return
        if not tgt or tgt == self.logged_acc:
            print("Invalid target.")
            wait_a_bit()
            return
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("SELECT name, email FROM accounts WHERE account_number=?", (tgt,))
        rr = c.fetchone()
        db.close()
        if not rr:
            print("Target acct not found.")
            wait_a_bit()
            return

        print(f"Sending to: {rr[0]}")
        try:
            amount = float(input("Amount: ").strip())
        except Exception:
            return
        if amount > 0 and curbal >= amount:
            if self.send_otp(self.user_mail, "Transfer", f"To: {rr[0]} (₹{amount})"):
                self.bump_bal(-amount)
                self.bump_target(tgt, amount)
                self.log_it("Transfer Sent", amount)
                self.log_target(tgt, "Transfer Received", amount)
                send_mail(self.user_mail, "Debit notif", f"₹{amount} sent to {rr[0]}.")
                send_mail(rr[1], "Credit notif", f"₹{amount} received from {self.whoami}.")
                print("Transfer done.")
        else:
            print("Not enough funds.")
        wait_a_bit()

    def statement(self):
        nice_head("Statement")

        # ----- FILTER SELECTION -----
        print("Filter: 1. All | 2. Deposit | 3. Withdrawal | 4. Transfer")
        f = input("Pick (1-4): ").strip()
        fmap = {'1': 'All', '2': 'Deposit', '3': 'Withdraw', '4': 'Transfer'}
        ft = fmap.get(f, "All")

        # ----- FETCH TRANSACTIONS -----
        db = sqlite3.connect("bank.db")
        c = db.cursor()

        query = """
            SELECT timestamp, type, amount
            FROM transactions
            WHERE account_number=?
        """
        params = [self.logged_acc]

        if ft != "All":
            query += " AND type LIKE ? "
            params.append(f"%{ft}%")

        query += " ORDER BY id DESC LIMIT 20"

        c.execute(query, params)
        rows = c.fetchall()
        db.close()

        # ----- DISPLAY RESULTS -----
        print(f"{'Date':<20} | {'Type':<20} | {'Amount':<10}")
        print("-" * 60)
        for date, ttype, amount in rows:
            print(f"{date:<20} | {ttype:<20} | ₹{amount:<10,.2f}")

        # ----- ASK FOR EMAIL COPY -----
        print()
        inp = input("Do you want a PDF copy of this statement sent to your email? (y/n): ").strip().lower()

        # wait_a_bit()

        if inp == "y":
            # Your existing PDF + email helper functions:
            pdf_name = f"statement_{self.logged_acc}.pdf"

            # Generate PDF using your method
            generate_statement_pdf(self.logged_acc, f, pdf_name)

            # Send the PDF as email attachment
            send_mail_pdf(
                dest_list=[self.user_mail],
                subject="Your Bank Statement",
                body="Attached is your requested bank statement.",
                pdf_path=pdf_name
            )

            print("A copy of the statement has been emailed to you.")
            wait_a_bit()


    def bens(self):
        nice_head("Beneficiaries")
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("SELECT name, ben_acc_num FROM beneficiaries WHERE owner_acc=?", (self.logged_acc,))
        for r in c.fetchall():
            print(f"- {r[0]} ({r[1]})")
        print("\n1. Add new | 0. Back")
        if input("Choice: ").strip() == '1':
            try:
                b = int(input("Beneficiary acct: ").strip())
            except Exception:
                db.close()
                return
            c.execute("SELECT name FROM accounts WHERE account_number=?", (b,))
            rr = c.fetchone()
            if rr and b != self.logged_acc:
                c.execute("INSERT INTO beneficiaries VALUES (NULL, ?, ?, ?)", (self.logged_acc, rr[0], b))
                db.commit()
                print("Added.")
            else:
                print("Bad acct or same as yours.")
        db.close()
        wait_a_bit()

    def apply_loan(self):
        nice_head("Loan apply")
        try:
            amount = float(input("Amount: ").strip())
        except Exception:
            return
        why = input("Purpose: ").strip()
        if len(why) == 0:
            print("Need a reason.")
            wait_a_bit()
            return
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("INSERT INTO loans (account_number, applicant_name, amount, purpose, status, request_date) VALUES (?, ?, ?, ?, ?, ?)",
                  (self.logged_acc, self.whoami, amount, why, 'Pending', datetime.now().strftime("%Y-%m-%d")))
        db.commit()
        db.close()
        send_mail(config.MANAGER_EMAIL, "Loan appl recvd", f"Applicant: {self.whoami}\nAmt: ₹{amount}\nPurpose: {why}")
        print("Application sent. We will check.")
        wait_a_bit()

    def check_loan(self):
        nice_head("Loan status")
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("SELECT request_date, amount, status FROM loans WHERE account_number=? ORDER BY loan_id DESC", (self.logged_acc,))
        print(f"{'Date':<12} | {'Amount':<10} | {'Status'}")
        for r in c.fetchall():
            print(f"{r[0]:<12} | ₹{r[1]:<9} | {r[2]}")
        db.close()
        wait_a_bit()

    def helpdesk(self):
        while True:
            nice_head("Help desk")
            print("1. Submit ticket")
            print("2. My tickets")
            print("3. Back")
            ch = input("Choice: ").strip()
            if ch == '1':
                q = input("What's up? ").strip()
                if len(q) == 0:
                    print("Say more please.")
                    continue
                db = sqlite3.connect("bank.db")
                c = db.cursor()
                c.execute("INSERT INTO helpdesk (account_number, applicant_name, query_text, request_date) VALUES (?, ?, ?, ?)",
                          (self.logged_acc, self.whoami, q, datetime.now().strftime("%Y-%m-%d")))
                db.commit()
                db.close()
                send_mail(config.MANAGER_EMAIL, "New help ticket", f"From: {self.whoami}\nQuery: {q}")
                print("Ticket made. we'll get back.")
            elif ch == '2':
                db = sqlite3.connect("bank.db")
                c = db.cursor()
                c.execute("SELECT request_date, status, query_text, resolution_text FROM helpdesk WHERE account_number=? ORDER BY ticket_id DESC", (self.logged_acc,))
                for r in c.fetchall():
                    print(f"\nDate: {r[0]} | Status: {r[1]}")
                    print(f"Q: {r[2]}")
                    if r[3]:
                        print(f"A: {r[3]}")
                    print("-" * 30)
                db.close()
                wait_a_bit()
            elif ch == '3':
                break

    def profile(self):
        nice_head("Your profile")
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("SELECT name, email, phone FROM accounts WHERE account_number=?", (self.logged_acc,))
        d = c.fetchone()
        db.close()
        print(f"Name:  {d[0]}")
        print(f"Email: {d[1]}")
        print(f"Phone: {d[2]}")
        print("\nUpdate: 1. Email | 2. Phone | 3. PIN | 0. Back")
        ch = input("Pick: ").strip()
        fmap = {'1': 'email', '2': 'phone', '3': 'pin'}
        if ch in fmap:
            nv = input(f"New {fmap[ch]}: ").strip()
            if self.send_otp(self.user_mail, "Profile update"):
                db = sqlite3.connect("bank.db")
                c = db.cursor()
                try:
                    c.execute(f"UPDATE accounts SET {fmap[ch]}=? WHERE account_number=?", (nv, self.logged_acc))
                    db.commit()
                    print("Updated.")
                    if ch == '1':
                        self.user_mail = nv
                except Exception:
                    print("Can't update, maybe value taken.")
                db.close()
                wait_a_bit()

    def bump_bal(self, amt):
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("UPDATE accounts SET balance = balance + ? WHERE account_number=?", (amt, self.logged_acc))
        db.commit()
        db.close()

    def bump_target(self, acct, amt):
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("UPDATE accounts SET balance = balance + ? WHERE account_number=?", (amt, acct))
        db.commit()
        db.close()

    def log_it(self, t, amt):
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("INSERT INTO transactions VALUES (NULL, ?, ?, ?, ?)", (self.logged_acc, t, amt, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        db.commit()
        db.close()

    def log_target(self, acct, t, amt):
        db = sqlite3.connect("bank.db")
        c = db.cursor()
        c.execute("INSERT INTO transactions VALUES (NULL, ?, ?, ?, ?)", (acct, t, amt, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        db.commit()
        db.close()