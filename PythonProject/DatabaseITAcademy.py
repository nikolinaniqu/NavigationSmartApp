import sqlite3

conn = sqlite3.connect('Books.db')
cursor = conn.cursor()



cursor.execute("""CREATE TABLE IF NOT EXISTS Books(
 id INT PRIMARY KEY, 
 title TEXT,
 year INT)
 """)

conn.commit()

def enterBooks():
    id=int(input("Please add the ID of the book:"))
    book_title=input("Please enter the title of the book:")
    year= int(input("Please enter the year of release:"))
    cursor.execute("INSERT INTO Books VALUES (?, ?,?)",(id,book_title,year))
    conn.commit()
enterBooks()

books = cursor.execute("SELECT * FROM Books")
print(books.fetchall())