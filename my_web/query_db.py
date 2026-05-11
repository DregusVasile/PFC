import sqlite3

conn = sqlite3.connect('shop.db')
c = conn.cursor()

# Get all table names
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print('Tables:', [t[0] for t in tables])

for table_name in [t[0] for t in tables]:
    print(f'\n{table_name.upper()}:')
    try:
        c.execute(f'SELECT * FROM {table_name} LIMIT 10')
        rows = c.fetchall()
        if rows:
            for row in rows:
                print(row)
        else:
            print('(empty)')
    except Exception as e:
        print(f'(error: {e})')

conn.close()