import sqlite3
conn = sqlite3.connect('data/manuals.sqlite')
cursor = conn.cursor()
cursor.execute("SELECT id, title FROM nodes WHERE level_label = 'LIBRO'")
print("LIBROS:")
for row in cursor.fetchall():
    print(row)

cursor.execute("SELECT id, level_label, title FROM nodes WHERE ordinal = 'I'")
print("CAPITULO 1:")
cap1 = cursor.fetchone()
print(cap1)
if cap1:
    cursor.execute("SELECT node_id, ordinal, SUBSTR(text, 1, 100) FROM chunks WHERE node_id = ?", (cap1[0],))
    print("CHUNKS DE CAPITULO 1:")
    for row in cursor.fetchall():
        print(row)
