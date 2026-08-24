import sqlite3

conn = sqlite3.connect('data/manuals.sqlite')
cursor = conn.cursor()

# Verificar el chunk del Capítulo II (node_id 4)
cursor.execute("SELECT id, level_label, title FROM nodes WHERE id = 4")
node = cursor.fetchone()
print(f"NODO: {node}\n")

cursor.execute("SELECT ordinal, SUBSTR(text, 1, 600) FROM chunks WHERE node_id = 4 AND ordinal = 0")
chunk = cursor.fetchone()
print(f"CHUNK #0:\n{chunk[1]}")
