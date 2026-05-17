import sqlite3
from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'db.sqlite3'
print('DB path:', p)
conn = sqlite3.connect(p)
cur = conn.cursor()
try:
    total = cur.execute('select count(*) from denuncias_denuncia').fetchone()[0]
    geo = cur.execute('select count(*) from denuncias_denuncia where latitude is not null and longitude is not null').fetchone()[0]
    print('total', total)
    print('with lat/lng', geo)
    for row in cur.execute('select id, titulo, latitude, longitude from denuncias_denuncia where latitude is not null and longitude is not null'):
        print(row)
except Exception as e:
    print('error', e)
finally:
    conn.close()
