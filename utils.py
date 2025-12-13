import os

import sqlite3
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import config

def send_mail_pdf(dest_list, subject, body, pdf_path):
    try:
        # Create the email container
        msg = MIMEMultipart()
        msg["From"] = config.SENDER_EMAIL
        msg["To"] = ", ".join(dest_list)
        msg["Subject"] = subject

        # Add body text
        msg.attach(MIMEText(body, "plain"))

        # Read the PDF file
        with open(pdf_path, "rb") as f:
            part = MIMEBase("application", "pdf")
            part.set_payload(f.read())

        # Encode to base64 for safe transfer
        encoders.encode_base64(part)

        # Add PDF header
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{pdf_path.split("/")[-1]}"'
        )

        msg.attach(part)

        # Connect to SMTP server
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)

        # Send email
        server.sendmail(config.SENDER_EMAIL, dest_list, msg.as_string())
        server.quit()

        # print("PDF email sent successfully!")

    except Exception as e:
        print("Failed to send the PDF email.")
        print("Error:", e)
        input()

def generate_statement_pdf(logged_acc, filter_type, filename="statement.pdf"):

    # Filter map (same as your CLI code)
    fmap = {'1': 'All', '2': 'Deposit', '3': 'Withdraw', '4': 'Transfer'}
    ft = fmap.get(filter_type, "All")

    # --- FETCH DATA FROM DB ---
    db = sqlite3.connect("bank.db")
    c = db.cursor()

    q = "SELECT timestamp, type, amount FROM transactions WHERE account_number=? "
    params = [logged_acc]

    if ft != "All":
        q += "AND type LIKE ? "
        params.append(f"%{ft}%")

    q += "ORDER BY id DESC LIMIT 20"

    c.execute(q, params)
    rows = c.fetchall()
    db.close()

    # --- BUILD PDF ---
    doc = SimpleDocTemplate(filename, pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("BANK STATEMENT", styles['Title']))
    story.append(Spacer(1, 20))

    # Account Info
    info = f"""
    <b>Account Number:</b> {logged_acc}<br/>
    <b>Filter Applied:</b> {ft}<br/>
    """
    story.append(Paragraph(info, styles["BodyText"]))
    story.append(Spacer(1, 20))

    # Table header
    table_data = [["Date", "Type", "Amount"]]

    # Add data rows (aligned with your print output)
    for date, ttype, amount in rows:
        table_data.append([
            date,
            ttype,
            f"Rs.{amount:,.2f}"
        ])

    # Table formatting
    table = Table(table_data, colWidths=[140, 150, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (2, 1), (2, -1), "RIGHT"),
    ]))

    story.append(table)

    doc.build(story)
    # print("PDF statement saved as:", filename)


# REMOVED the global winsound import to prevent crashes on Mac
def send_mail_multi(dest_list, subject, body):
    try:
        m = MIMEText(body)
        m['Subject'] = subject
        m['From'] = config.SENDER_EMAIL
        m['To'] = ", ".join(dest_list)

        s = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        s.starttls()
        s.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)

        s.sendmail(config.SENDER_EMAIL, dest_list, m.as_string())
        s.quit()

    except Exception as e:
        print("Failed to send mail to multiple recipients.")
        print(e)
        input()
def clr_scr():
    os.system('cls' if os.name == 'nt' else 'clear')

def wait_a_bit():
    input("\nPress Enter to continue...")

def nice_head(txt):
    clr_scr()
    print("=" * 50)
    print(f"  {txt}")
    print("=" * 50)
    print()
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import config
from reportlab.pdfgen import canvas

def create_pdf(filename):
    c = canvas.Canvas(filename)
    c.drawString(100, 750, "Hello, this is a PDF created with ReportLab!")
    c.save()

create_pdf("example.pdf")

def send_mail_with_pdf(dest_list, subject, body, pdf_path):
    try:
        # Create the email container
        msg = MIMEMultipart()
        msg['From'] = config.SENDER_EMAIL
        msg['To'] = ", ".join(dest_list)
        msg['Subject'] = subject

        # Add email body
        msg.attach(MIMEText(body, 'plain'))

        # Open the PDF file
        with open(pdf_path, 'rb') as f:
            part = MIMEBase('application', 'pdf')
            part.set_payload(f.read())

        encoders.encode_base64(part)  # required encoding
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{pdf_path.split("/")[-1]}"'
        )

        msg.attach(part)

        # Send through SMTP
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)

        server.sendmail(config.SENDER_EMAIL, dest_list, msg.as_string())
        server.quit()

        print("Email sent successfully.")

    except Exception as e:
        print("Failed to send email.")
        print("Error:", e)
        input()

def send_mail(dest, subject, body):
    try:
        m = MIMEText(body)
        m['Subject'] = subject
        m['From'] = config.SENDER_EMAIL
        m['To'] = dest
        s = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        s.starttls()
        s.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
        s.sendmail(config.SENDER_EMAIL, [dest], m.as_string())
        s.quit()
    except Exception:
        pass

def play_cash():
    """
    Plays a sound on both Windows and Mac without external libraries.
    """
    if os.name == 'nt':  # Windows
        try:
            import winsound
            winsound.Beep(1000, 100)
            winsound.Beep(2000, 300)
        except ImportError:
            pass
            
    # else:  # Mac / Linux / iPhone
    #     # macOS uses 'afplay' to play system files. 
    #     # 'Glass.aiff' is a standard clean 'ping' sound on all Macs.
    #     os.system('afplay /System/Library/Sounds/Glass.aiff')
        
    #     # ALTERNATIVE: If you want a voice instead of a beep on Mac:
    #     # os.system('say "Cha Ching"')