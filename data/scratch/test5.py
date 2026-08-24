import sqlite3
import json
import pickle

conn = sqlite3.connect('data/manuals.sqlite')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(manuals)')
cols = [r[1] for r in cursor.fetchall()]
print("Cols in manuals:", cols)

if 'tree' in cols:
    cursor.execute('SELECT tree FROM manuals WHERE id=1')
elif 'hierarchy_tree' in cols:
    cursor.execute('SELECT hierarchy_tree FROM manuals WHERE id=1')
else:
    print("NO TREE COLUMN")
    exit()

res = cursor.fetchone()
if res:
    tree = pickle.loads(res[0])
    n2 = next((n for n in tree.nodes if n.local_id==2), None)
    n3 = next((n for n in tree.nodes if n.local_id==3), None)
    print("N2 indices:", n2.body_element_indices if n2 else None)
    print("N3 indices:", n3.body_element_indices if n3 else None)
