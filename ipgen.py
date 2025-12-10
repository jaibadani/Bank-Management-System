def gen(receiver):
    import subprocess
    import smtplib
    class config:
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        SENDER_EMAIL = "ciaobank.loan.approval@gmail.com"
        SENDER_PASSWORD = "guum lfdx qaiz sxbv"
        MANAGER_EMAIL = "jaibadani28@gmail.com"
    from email.mime.text import MIMEText
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
    # This runs the command and captures the text output
    val = subprocess.getoutput("ipconfig getifaddr en0")
    send_mail(receiver, "IP Address", f"My IP Address is: {val}")
    # print(f"My IP Address is: {val}")