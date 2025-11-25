import os
import smtplib
from email.mime.text import MIMEText
import config

try:
    import winsound
    SOUND_ENABLED = True
except ImportError:
    SOUND_ENABLED = False

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
    if SOUND_ENABLED:
        try:
            winsound.Beep(1000, 100)
            winsound.Beep(2000, 300)
        except Exception:
            pass