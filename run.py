from database import mk_db
from bank import Bank

mk_db()
app = Bank()
app.start()
print("\nbye bye, take care!")