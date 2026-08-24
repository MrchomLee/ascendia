import sqlite3
import json
conn = sqlite3.connect('data/manuals.sqlite')
cursor = conn.cursor()

def get_node_info(node_id):
    cursor.execute("SELECT level_label, title FROM nodes WHERE id = ?", (node_id,))
    label, title = cursor.fetchone()
    print(f"NODE {node_id}: {label} {title}")
    cursor.execute("SELECT text FROM chunks WHERE node_id = ?", (node_id,))
    for chunk in cursor.fetchall():
        print(f"  CHUNK: {repr(chunk[0][:100])}")

get_node_info(2) # Titulo Primero
get_node_info(3) # Capitulo I
