import sqlite3
conn = sqlite3.connect('data/manuals.sqlite')
cursor = conn.cursor()
cursor.execute("SELECT text FROM chunks WHERE text LIKE '%(Se deroga)%'")
results = cursor.fetchall()
print(f"Encontrados: {len(results)}")
for r in results:
    print(repr(r[0]))
