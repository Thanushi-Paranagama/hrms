import sqlite3, shutil, time
shutil.copy('db.sqlite3', f'db.sqlite3.bak.{int(time.time())}')
con=sqlite3.connect('db.sqlite3')
cur=con.cursor()
threshold = 10**8 - 1
print('threshold', threshold)
cur.execute('SELECT id, salary_base FROM employees_employee WHERE salary_base IS NOT NULL AND CAST(salary_base AS REAL) > ?', (threshold,))
rows = cur.fetchall()
print('rows to fix:', rows)
if rows:
    cur.executemany('UPDATE employees_employee SET salary_base = ? WHERE id = ?', [('0.00', r[0]) for r in rows])
    con.commit()
    print('applied fixes to large values')
else:
    print('no large numeric values found')
con.close()
