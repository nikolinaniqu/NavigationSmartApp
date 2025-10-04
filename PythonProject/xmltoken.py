import sqlite3

conn = sqlite3.connect('example.db')
cursor = conn.cursor()



cursor.execute("""CREATE TABLE IF NOT EXISTS Users(
 id INT PRIMARY KEY, 
 username TEXT,
 password TEXT,
 token TEXT)
 """)

conn.commit()

users = cursor.execute("SELECT * FROM Users")

if (len(users.fetchall()) == 0):

         user = [('1', 'user1', 'pwd1', ''), ('2', 'user2', 'pwd2', ''),
                 ('3', 'user3', 'pwd3', '')]

         cursor.executemany("INSERT INTO Users VALUES (?, ?, ?, ?)", user)

         conn.commit()