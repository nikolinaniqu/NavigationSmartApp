import sqlite3
import datetime
import jwt

# Connect and create the table
conn = sqlite3.connect("clients.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Clients (
        id INT PRIMARY KEY,
        NameandSurname TEXT,
        Account TEXT,
        Password TEXT,
        Token TEXT
    )
""")
conn.commit()

# Sample data (optional: use INSERT OR IGNORE to avoid re-inserting on rerun)
clients = [
    (1, "Marc Swarowski", "1010203040", "max12345", " "),
    (2, "Nikolina Milic", "2080604355", "nikol123", " "),
    (3, "Mario Milojevic", "1234789077", "mario223", " ")
]

cursor.executemany("INSERT OR IGNORE INTO Clients VALUES (?, ?, ?, ?, ?)", clients)
conn.commit()

# Define function
def check_client():
    account = input("Please enter your account number: ")
    password = input("Please enter your password: ")

    cursor.execute("SELECT * FROM Clients WHERE Account=? AND Password=?", (account, password))
    client = cursor.fetchone()

    if not client:
        print("The account number and password do not exist in the database.")
    else:
        secret_key = "Nostardamus"
        payload = {
            "Account": account,
            "Password": password,
            "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=45),
            "iat": datetime.datetime.now(datetime.UTC)
        }

        token = jwt.encode(payload, secret_key, algorithm="HS256")

        cursor.execute("UPDATE Clients SET Token=? WHERE Account=? AND Password=?", (token, account, password))
        conn.commit()
        print("Token generated and stored in the database:")
        print(token)

# Run the function
check_client()

# Close connection
conn.close()
