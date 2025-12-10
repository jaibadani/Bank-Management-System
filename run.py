from database import mk_db
from bank import Bank

mk_db() # ye apna databbase banayega if not exists
app = Bank() # creates ab object of bank class
app.start() # enjoy
print("\nbye bye, take care darlin!")