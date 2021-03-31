

from ..helpers import path, db, config, timestamp
import os

def listMigrations():
  return os.listdir(path.appendDirToRootDir('migrations'))

def getMigrationNames():
  migFolderFiles = listMigrations()
  splitFiles = [f.split(".") for f in migFolderFiles]
  filteredFiles = [f for f in splitFiles if len(f) == 4 and f[3] == "mign"]
  rejoinedFiles = [".".join(f) for f in filteredFiles]
  return filteredFiles, rejoinedFiles

class Migration:
  def __init__(self, name, parts):
    self.__path = path.appendFileToDir(path.appendDirToRootDir('migrations'), name)
    self.__nameParts = parts
    # name parts
    # 0 - TYPE: create, edit, drop
    # 1 - NAME: table name
    # 2 - TIMESTAMP: unix timestamp from migration file generation time
    # 3 - SUFFIX: file ending, i.e. mign
    if self.__nameParts[0] != "create" and self.__nameParts[0] != "edit" and self.__nameParts != "drop":
      self.valid = False
    else:
      self.valid = True
    self.__lines = self.__ripData()
    self.__parseIndexes()
    self.__generateUpQuery()
    self.__generateDownQuery()
    
  def up(self):
    self.__upQuery.execute()
    
  def down(self):
    self.__downQuery.execute()
    
  def getTimestamp(self):
    return timestamp.floatTsFromHyphenFormat(self.__nameParts[2])
    
  def getNameWOExt(self):
      return f'{self.__nameParts[0]}.{self.__nameParts[1]}.{self.__nameParts[2]}'
      
  def __ripData(self):
    lines = []
    file = open(self.__path, 'r')
    for line in file:
      lines.append(line.rstrip('\n'))
    file.close()
    return lines

  def __parseIndexes(self):
    if self.__lines[0] != "UP" or "DOWN" not in self.__lines:
      self.valid = False
      return
    else:
      # index of first line after "UP"
      self.__upstart = 1
      currVal = self.__lines[1]
      currIdx = 1
      while currVal != "DOWN":
        currIdx += 1
        currVal = self.__lines[currIdx]
      # index of line before "DOWN"
      self.__upend = currIdx - 1
      currIdx += 1
      # index of first line after "DOWN"
      self.__downstart = currIdx
      currVal = self.__lines[currIdx]
      # index of last line
      self.__downend = len(self.__lines) - 1

  def __generateUpQuery(self):
    self.__upQuery = self.__parseLines(self.__upstart, self.__upend, 'up')

  def __generateDownQuery(self):
    self.__downQuery = self.__parseLines(self.__downstart, self.__downend, 'down')
    
  def __parseLines(self, first, last, upOrDown):
    cols = []
    comp = []
    foreigns = []
    alters = []
    res = None
    for i in range(first, last + 1):
      parts = self.__lines[i].split('~')
      if parts[0] == 'col':
        cols.append((parts[1],parts[2]))
      elif parts[0] == 'comp':
        names = parts[1].split(',')
        for n in names:
          comp.append(n)
      elif parts[0] == 'foreign':
        foreigns.append({
          'name': parts[1],
          'reference': (parts[2], parts[3])
        })
      elif parts[0] == 'timestamps':
        cols.append(('created_at','REAL NOT NULL'))
        cols.append(('updated_at','REAL'))
      elif parts[0] == 'drop-table':
        res = db.Query(db.DropTableStatement(self.__nameParts[1]))
        return res
      else:
        alters.append(":".join(parts))
    if self.__nameParts[0] == 'create':
      compArg = comp if len(comp) > 0 else None
      forArg = foreigns if len(foreigns) > 0 else None 
      res = db.Query(db.CreateTableStatement(self.__nameParts[1],cols, compArg, forArg))
    elif self.__nameParts[0] == 'edit':
      statements = []
      for i in range(0, len(alters)):
        statements.append(db.AlterTableStatement(self.__nameParts[1], alters[i], upOrDown))
      res = db.Queries(statements)
    elif self.__nameParts[0] == 'drop':
      res = db.Query(db.DropTableStatement(self.__nameParts[1]))
    return res

def parseMigrationFiles():
  splits, strs = getMigrationNames()
  migrations = []
  for i in range(len(splits)):
    migrations.append(Migration(strs[i],splits[i]))
    
migrationTableQuery = 'CREATE TABLE IF NOT EXISTS migration (id INTEGER PRIMARY KEY NOT NULL, name TEXT NOT NULL, batch INTEGER NOT NULL)'

def getLastBatchNumber():
  conn = db.Connection()
  res = conn.cursor.execute('SELECT MAX(batch) FROM migration').fetchone()[0]
  del conn
  return res

def getNextBatchNumber():
  return getLastBatchNumber() + 1
  
def sortMigrationsAsc(ml):
  ch = True
  while ch:
    ch = False
    for i in range(0,len(ml)-1):
      if ml[i].getTimestamp() > ml[i+1].getTimestamp():
        tmp = ml[i]
        ml[i] = ml[i+1]
        ml[i+1] = tmp 
        ch = True
  return ml 
  
def sortMigrationsDsc(ml):
  ch = True
  while ch:
    ch = False
    for i in range(0,len(ml)-1):
      if ml[i].getTimestamp() < ml[i+1].getTimestamp():
        tmp = ml[i]
        ml[i] = ml[i+1]
        ml[i+1] = tmp 
        ch = True
  return ml
  
def getSortedListMigrations(dr = 'asc'):
  f, r = getMigrationNames()
  m = []
  for i in range(0,len(f)):
    m.append(Migration(r[i], f[i]))
  sm = sortMigrationsAsc(m) if dr == 'asc' else sortMigrationsDsc(m)
  return sm
  
def migrate():
  conn = db.Connection()
  conn.cursor.execute(migrationTableQuery)
  anyMigs = True if conn.cursor.execute('SELECT COUNT(*) FROM migration').fetchone()[0] > 0 else False
  del conn 
  sm = getSortedListMigrations()
  if anyMigs:
    # some migrations have already been run so we need to sort migrations
    # get list of timestamps in db 
    conn = db.Connection()
    res = conn.cursor.execute('SELECT name FROM migration').fetchall()
    res = [timestamp.floatTsFromHyphenFormat(rec[0].split('.')[2]) for rec in res]
    del conn 
    # filter out migrations whose timestamps are in the list from db
    fm = [mig for mig in sm if mig.getTimestamp() not in res]
    # execute remaining migrations
    nb = getNextBatchNumber()
    if len(fm) > 0:
      print(f'Migrating (batch {nb})...')
    else:
      print("No new migrations to run.")
    for om in fm:
      print(f'UP - {om.getNameWOExt()}')
      om.up()
      # record migration 
      conn = db.Connection()
      conn.cursor.execute('INSERT INTO migration (name, batch) VALUES (?, ?)', (om.getNameWOExt(),nb))
      del conn
  else:
    # run all migrations 
    print("Migrating (batch 1)...")
    nb = 1
    for mig in sm:
      print(f'UP - {mig.getNameWOExt()}')
      mig.up()
      # record migration 
      conn = db.Connection()
      conn.cursor.execute('INSERT INTO migration (name, batch) VALUES (?, ?)', (mig.getNameWOExt(),nb))
      del conn 
      
def rollback():
  conn = db.Connection()
  conn.cursor.execute(migrationTableQuery)
  anyMigs = True if conn.cursor.execute('SELECT COUNT(*) FROM migration').fetchone()[0] > 0 else False
  del conn 
  if anyMigs:
    sm = getSortedListMigrations('d')
    lb = getLastBatchNumber()
    print(f'Rolling Back Migrations (batch {lb})...')
    conn = db.Connection()
    res = conn.cursor.execute(f'SELECT name FROM migration WHERE batch = {lb}').fetchall()
    del conn
    res = [timestamp.floatTsFromHyphenFormat(rec[0].split('.')[2]) for rec in res]
    filtered = [m for m in sm if m.getTimestamp() in res]
    for r in filtered:
      print(f'DOWN - {r.getNameWOExt()}')
      r.down()
      conn = db.Connection()
      conn.cursor.execute(f'DELETE FROM migration WHERE batch = {lb}')
      del conn
    
def refresh():
  dbname = config.get('db.current')
  dbpath = config.get(f'db.list.{dbname}')
  dbpath = path.appendFileToRootDir(dbpath)
  if os.path.exists(dbpath):
    os.remove(dbpath)
  migrate()

def schema(p = True, cs = config.get(f'db.list.{config.get("db.current")}')):
  conn = db.Connection(False, cs)
  conn.cursor.execute(migrationTableQuery)
  tables = conn.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
  del conn
  res = {}
  if p:
    print("TABLES")
  for t in tables:
    if p:
      print(t[0])
    conn = db.Connection()
    conn.cursor.execute(f'PRAGMA table_info({t[0]})')
    cols = conn.cursor.fetchall()
    del conn
    res[t[0]] = {}
    for c in cols:
      if p:
        print(f'+ {c[1]} {c[2]} {c[3]}')
      else:
        res[t[0]][c[1]] = {
          'type': c[2],
          'nullable': True if c[3] < 1 else False
        }
  return res


def generateMigrationFile(migType, migTarget):
  ts = timestamp.hyphenatedTsStr()
  fn = f'{migType}.{migTarget}.{ts}.mign'
  p = path.appendDirToRootDir('migrations')
  p = path.appendFileToDir(p, fn)
  outfile = open(p, 'w')
  outfile.write('UP\n\nDOWN\n')
  outfile.close()