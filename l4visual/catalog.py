import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_FILE = ROOT / 'resources' / 'catalog.sqlite3'

class Catalog:
    def __init__(self, db_path=DB_FILE):
        if not Path(db_path).is_file():
            raise FileNotFoundError(f'缺少 API 数据库：{db_path}；请运行 python tools/build_catalog.py')
        self.connection = sqlite3.connect(str(db_path))
        self.connection.row_factory = sqlite3.Row

    def events(self, search=''):
        q = '%' + search + '%'
        return [dict(r) for r in self.connection.execute(
            'SELECT name,category,fields,source FROM events WHERE name LIKE ? ORDER BY name', (q,))]

    def methods(self, search='', owner=None):
        q = '%' + search + '%'
        if owner:
            return [dict(r) for r in self.connection.execute(
                'SELECT * FROM methods WHERE (name LIKE ? OR owner LIKE ?) AND owner = ? ORDER BY name', (q, q, owner))]
        return [dict(r) for r in self.connection.execute(
            'SELECT * FROM methods WHERE name LIKE ? OR owner LIKE ? ORDER BY owner,name', (q, q))]

    def method(self, owner, name):
        row = self.connection.execute(
            'SELECT * FROM methods WHERE owner=? AND name=?', (owner, name)).fetchone()
        return dict(row) if row else None

    def prop_tables(self, search=''):
        return [dict(r) for r in self.connection.execute('SELECT * FROM sendtables WHERE name LIKE ? ORDER BY name', ('%'+search+'%',))]

    def props(self, table='', search='', include_inherited=True):
        table = table.strip()
        if not table:
            return [dict(r) for r in self.connection.execute(
                'SELECT * FROM netprops WHERE name LIKE ? ORDER BY name LIMIT 250', ('%'+search+'%',))]
        names = [table]
        if include_inherited:
            seen = {table}
            while True:
                row = self.connection.execute('SELECT base FROM sendtables WHERE name = ?', (names[-1],)).fetchone()
                if not row or not row['base'] or row['base'] in seen:
                    break
                names.append(row['base'])
                seen.add(row['base'])
        marks = ','.join('?' for _ in names)
        return [dict(r) for r in self.connection.execute(
            f'SELECT * FROM netprops WHERE table_name IN ({marks}) AND name LIKE ? ORDER BY name', (*names,'%'+search+'%'))]

    def stats(self):
        return {table: self.connection.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]
                for table in ('events','methods','sendtables','netprops')}

    def close(self):
        self.connection.close()
