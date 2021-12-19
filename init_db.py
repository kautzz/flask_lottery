import sqlite3
import secrets

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO posts (code, name, country, city, content, start, until) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ('000000', 'Martin', 'Spanien', 'Alfinach / GARAGE', 'Zum testen der APP', 'April', 'August')
            )

cur.execute("INSERT INTO images (code, filename) VALUES (?, ?)",
            ('000000', 'temp.jpg')
            )

for k in range(6):
    s = secrets.token_hex(3)
    print(s)
    cur.execute("INSERT INTO tickets (ticket_id, valid) VALUES (?, ?)",
                (s, '1')
                )

connection.commit()
connection.close()
