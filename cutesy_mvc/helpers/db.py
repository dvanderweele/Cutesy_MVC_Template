import sqlite3, collections
from ..helpers import config, path 

# SQLite Data Types
# 0 - NULL
# 1 - INTEGER
# 2 - REAL 
# 3 - TEXT 
# 4 - BLOB
dataTypes = ('NULL', 'INTEGER', 'REAL', 'TEXT', 'BLOB')

class Connection:
  def __init__(self, rf = False, tc = config.get(f'db.list.{config.get("db.current")}')):
    self.__path = path.appendFileToRootDir(tc)
    self.__conn = sqlite3.connect(self.__path)
    if rf:
      self.__conn.row_factory = sqlite3.Row
    self.cursor = self.__conn.cursor()
    self.cursor.execute('PRAGMA foreign_keys=ON')
  def __del__(self):
    self.__conn.commit() 
    self.__conn.close() 

class Query:
  def __init__(self, statementObj):
    self.__statement = statementObj
  def execute(self):
    self.__conn = Connection()
    if not self.__statement.getParamList():
      self.__conn.cursor.execute(self.__statement.getQueryString())
    else:
      self.__conn.cursor.execute(self.__statement.getQueryString(), self.__statement.getParamList())
    del self.__conn

class Queries:
  def __init__(self, statements):
    self.__statements = statements
  def execute(self):
    self.__conn = Connection()
    for q in self.__statements:
      print(q.getQueryString())
      if not q.getParamList():
        self.__conn.cursor.execute(q.getQueryString())
      else:
        self.__conn.cursor.execute(q.getQueryString(), q.getParamList())
    del self.__conn

class CreateTableStatement:
  def __init__(self, tableName, columns, composite = None, foreigns = None):
    # columns should be a tuple of tuples, with each inner tuple 
    # having length 2 and representing a column name and datatype string
    # if non-null composite is provided, it is a one dimensional tuple of column names
    # if non-null foreigns is provided, it is a list of dictionaries where name key is column name in this table and reference key is a tuple of length two w/ 1st val being table name and 2nd being column name
    self.__tableName = tableName

    self.__columns = columns
    self.__composite = composite
    self.__foreigns = foreigns
  def getQueryString(self):
    res = f'CREATE TABLE IF NOT EXISTS {self.__tableName} ('
    for i in range(0, len(self.__columns)):
      res += f'{self.__columns[i][0]} {self.__columns[i][1]}'
      if i != len(self.__columns) - 1:
        res += ', '
    if self.__composite != None:
      res += ', PRIMARY KEY('
      for i in range(0, len(self.__composite)):
        if i != 0:
          res += ', '
        res += self.__composite[i]
      res += ')'
    if self.__foreigns != None:
      res += ','
      for i in range(0, len(self.__foreigns)):
        if i != 0 and i < len(self.__foreigns) - 1:
          res += ','
        k1 = self.__foreigns[i]['name']
        tn = self.__foreigns[i]['reference'][0]
        k2 = self.__foreigns[i]['reference'][1]
        res += f' FOREIGN KEY({k1}) REFERENCES {tn}({k2})'
        if i != len(self.__foreigns) - 1:
          res += ', '
    res += ')'
    return res
  def getParamList(self):
    return False
    
class DropTableStatement:
  def __init__(self, tableName):
    self.__tableName = tableName
  def getQueryString(self):
    return f'DROP TABLE IF EXISTS {self.__tableName}'
  def getParamList(self):
    return False
    
class AlterTableStatement:
  def __init__(self, tablename, line, upOrDown):
    self.__line = line.split(":")
    self.__tableName = tablename if self.__line[0] == 'rntab' and upOrDown == 'up' else self.__line[1]
  def getQueryString(self):
    # no support for sqlite's add column function because then we would have to emulate drop column functionality, which isn't directly supported
    # only support for renaming a column or a table 
    res = f"ALTER TABLE {self.__tableName} RENAME TO {self.__line[2]}"
    return res
  def getParamList(self):
    return False
    
class Where: 
  def __init__(self, conditions = []):
    self.__conditions = conditions
    self.__params = []
    self.__parsed = False
  
  def __str__(self):
  	self.parse()
  	res = f'WHERE OBJECT:\nCondition String: {self.__string}\nParameters: '
  	for i in range(0,len(self.__params)):
  		res += str(self.__params[i])
  		if i < len(self.__params) - 1:
  			res += '; '
  	return res
  
  def parse(self):
    if not self.__parsed:
      self.__string = self.__buildConditionString()
      self.__parsed = True
    
  def __buildConditionString(self):
    res = 'WHERE '
    self.__params = []
    for i in range(0, len(self.__conditions)):
    	res += self.__processConditionRecord(self.__conditions[i], i)
    return res
    
  def getConditionString(self):
    return self.__string
    
  def getParams(self):
    return self.__params
    
  def prependCondition(self, conditionDict, operator = 'AND'):
    self.__parsed = False 
    self.__conditions.insert(0,conditionDict)
    if len(self.__conditions) > 1:
      self.__conditions[1]['operator'] = operator
    self.parse()
        
  def setCondition(self, index, conditionDict):
    self.__parsed = False
    self.__conditions[index] = conditionDict
    
  def __processConditionRecord(self, rec, idx):
    res = ''
    if rec['type'] == 'single':
      if idx != 0:
        res+= f' {rec["operator"]} '
      res += f'({rec["condition"][0]} {rec["condition"][1]}'
      if type(rec['condition'][2]) is not str and isinstance(rec['condition'][2], collections.abc.Sequence):
        res+='('
        for i in range(0,len(rec['condition'][2])):
          res+= '?'
          self.__params.append(rec['condition'][2][i])
          if i < len(rec['condition'][2]) - 1:
            res+=', '
        res+=')'
      else:
        res += ' ?'
        self.__params.append(rec['condition'][2])
      res += ')'
    elif rec['type'] == 'series':
      if idx != 0:
        res+= f' {rec["operator"]} '
      res += '('
      for i in range(len(rec['series'])):
        res += self.__processConditionRecord(rec['series'][i], i)
      res += ')'
    elif rec['type'] == 'not':
      if idx != 0:
        res+= f' {rec["operator"]} '
      res += 'NOT('
      for i in range(len(rec['not'])):
        res += self.__processConditionRecord(rec['not'][i], i)
      res += ')'
    return res 

class Table:
  def __init__(self, tableName = ''):
    self.__table = tableName
    self.__statement = ''
    self.__params = []
    self.__finalized = False
    self.__conditions = None
    self.__columns = []
    self.__type = None
    self.__ordering = []
    self.__limit = None
    self.__offset = None
    self.__distinct = False
    self.__values = []
    self.__connection = config.get(f'db.list.{config.get("db.current")}')
  
  def __buildStatement(self):
    if self.__conditions != None:
      self.__conditions.parse()
    if self.__type == 'sel':
      self.__statement += 'SELECT '
      if self.__distinct:
        self.__statement += ' DISTINCT '
      for i in range(len(self.__columns)):
        if i != 0:
          self.__statement += ', '
        self.__statement += f'{self.__columns[i]}'
      self.__statement += f' FROM {self.__table}'
      if self.__conditions != None:
        self.__statement += ' '
        self.__statement += self.__conditions.getConditionString()
        for p in self.__conditions.getParams():
          self.__params.append(p)
      if len(self.__ordering) > 0:
        for o in self.__ordering:
          self.__statement += f' ORDER BY {o[0]}'
          if o[1] != 'asc':
            self.__statement += ' DESC'
      if self.__limit is not None:
        self.__statement += ' LIMIT ?'
        self.__params.append(self.__limit)
      if self.__offset is not None:
        self.__statement += ' OFFSET ?'
        self.__params.append(self.__offset)
    elif self.__type == 'ins':
      self.__statement += f'INSERT INTO {self.__table} ('
      for i in range(0,len(self.__columns)):
        if i > 0:
          self.__statement += ', '
        self.__statement += self.__columns[i]
      self.__statement += ') VALUES('
      for i in range(0,len(self.__values)):
        if len(self.__values) > 1:
          self.__statement +='('
        for j in range(0, len(self.__values[i])):
          if j > 0:
            self.__statement += ', '
          self.__statement += '?'
          self.__params.append(self.__values[i][j])
        if len(self.__values) > 1:
          self.__statement += ')'
          if i < len(self.__values) - 1:
            self.__statement += ', '
        self.__statement += ')'
    elif self.__type == 'upd':
      self.__statement += f'UPDATE {self.__table} SET'
      for i in range(0, len(self.__columns)):
        if i > 0:
          self.__statement += ','
        self.__statement += f' {self.__columns[i]} = ?'
        self.__params.append(self.__values[i])
      if self.__conditions is not None:
        self.__statement += ' '
        self.__statement += self.__conditions.getConditionString()
        for p in self.__conditions.getParams():
          self.__params.append(p)
      if len(self.__ordering) > 0:
        for o in self.__ordering:
          self.__statement += f' ORDER BY {o[0]}'
          if o[1] != 'asc':
            self.__statement += ' DESC'
      if self.__limit is not None:
        self.__statement += ' LIMIT ?'
        self.__params.append(self.__limit)
      if self.__offset is not None:
        self.__statement += ' OFFSET ?'
        self.__params.append(self.__offset)
    elif self.__type == 'del':
      self.__statement += f'DELETE FROM {self.__table}'
      if self.__conditions is not None:
        self.__statement += ' '
        self.__statement += self.__conditions.getConditionString()
        for p in self.__conditions.getParams():
          self.__params.append(p)
      if len(self.__ordering) > 0:
        for o in self.__ordering:
          self.__statement += f' ORDER BY {o[0]}'
          if o[1] != 'asc':
            self.__statement += ' DESC'
      if self.__limit is not None:
        self.__statement += ' LIMIT ?'
        self.__params.append(self.__limit)
      if self.__offset != None:
        self.__statement += ' OFFSET ?'
        self.__params.append(self.__offset)
    self.__finalizeStatement()
  
  def __finalizeStatement(self):
    if self.__type != None:
      self.__finalized = True

  def __execute(self):
    res = []
    if self.__finalized:
      conn = Connection(True)
      res = conn.cursor.execute(self.__statement, self.__params).fetchall()
      del conn
      return res
      
  def setConnection(self, conn):
    self.__connection = conn 
    return self
  
  def columns(self,cols):
    for c in cols:
      self.__columns.append(c)
    return self

  def find(self, id):
    self.__type = 'sel'
    w = {
      'type': 'single',
      'condition': ('id', '=', id)
    }
    if self.__conditions == None:
      self.__conditions = Where([])
    self.__conditions.prependCondition(w)
    self.__columns.append('*')
    self.__limit = '1'
    self.__buildStatement()
    return self.__execute()

  def first(self):
    self.__type = 'sel'
    self.__limit = '1'
    if len(self.__columns) < 1:
      self.__columns.append('*')
    self.__buildStatement()
    return self.__execute()

  def value(self, col):
    self.__type = 'sel'
    self.__columns.append(col)
    self.__limit = '1'
    self.__buildStatement()
    return self.__execute()
  
  def pluck(self, col):
    self.__type = 'sel'
    self.__columns.append(col)
    self.__buildStatement() 
    return self.__execute() 
  
  def conditions(self, w):
    self.__conditions = w
    return self

  def condition(self,col,op,val):
    w = Where([{'type':'single','condition':(col,op,val)}])
    self.__conditions = w 
    return self 
    
  def limit(self,num):
    self.__limit = num 
    return self 

  def get(self):
    if self.__type == None:
      self.__type = 'sel'
    if len(self.__columns) < 1:
      self.__columns.append('*')
    self.__buildStatement() 
    return self.__execute()

  def distinct(self):
    self.__distinct = True 
    return self
  
  def orderBy(self, col, dr = 'asc'):
    self.__ordering.append((col, dr))
    return self 
    
  def chunk(self, size, cb):
    if self.__type == None:
      self.__type = 'sel'
    if len(self.__columns) < 1:
      self.__columns.append('*')
    self.__limit = size
    self.__offset = 0
    self.__buildStatement() 
    res = self.__execute()
    discontinue = False
    for rec in res:
      if not cb(rec):
        discontinue = True
    while len(res) > 0 and not(discontinue):
      self.__offset += size + 1
      self.__statement = ""
      self.__params = []
      self.__buildStatement()
      res = self.__execute()
      for rec in res:
        if not cb(rec):
          discontinue = True
          break
      
  def chunkById(self, size, cb):
    if self.__type == None:
      self.__type = 'sel'
    if len(self.__columns) < 1:
      self.__columns.append('*')
    self.orderBy('id').limit(size)
    last = 0
    if self.__conditions == None:
      self.__conditions = Where([])
    self.__conditions.prependCondition({'type':'single','condition':('id','<',last)})
    self.__buildStatement() 
    res = self.__execute()
    discontinue = False
    for rec in res:
      last = rec['id']
      if not cb(rec):
        discontinue = True
    while len(res)>0 and not discontinue:
      self.__conditions.setCondition(0,{'type':'single','condition':('id','>',last)})
      self.__statement = ""
      self.__params = []
      self.__buildStatement() 
      res = self.__execute()
      for rec in res:
        last = rec['id']
        if not cb(rec):
          discontinue = True
          break
      
  # insert 
  def insert(self, columns, values):
    self.__type = 'ins'
    self.__columns = columns 
    self.__values = values 
    self.__buildStatement()
    self.__execute()
  
  # insertGetId 
  def insertGetId(self, columns, values):
    self.__type = 'ins'
    self.__columns = columns 
    self.__values = values 
    self.__buildStatement()
    res = None
    if self.__finalized:
      conn = Connection(True)
      conn.cursor.execute(self.__statement, self.__params)
      res = conn.cursor.lastrowid
      del conn
    return res

  # update 
  def update(self, columns, values):
    self.__type =  'upd'
    if len(columns) != len(values):
      return None
    for i in range(0, len(columns)):
      self.__columns.append(columns[i])
      self.__values.append(values[i])
    self.__buildStatement()
    self.__execute()
    
  def count(self, col='*'):
    self.__type = 'sel'
    self.__columns.append(f'Count({col})')
    self.__buildStatement()
    return self.__execute()[0][0]
  
  #exists 
  def exists(self):
    return True if self.count('*') > 0 else False
  
  #doesntExist
  def doesntExist(self):
    return not self.exists()
    
  def maximum(self, col):
    self.__type = 'sel'
    self.__columns.append(f'Max({col})')
    self.__buildStatement()
    return self.__execute()[0][0]
  
  def minimum(self, col):
    self.__type = 'sel'
    self.__columns.append(f'Min({col})')
    self.__buildStatement()
    return self.__execute()[0][0]
   
  
  def average(self, col):
    self.__type = 'sel'
    self.__columns.append(f'Avg({col})')
    self.__buildStatement()
    return self.__execute()[0][0]
  
  
  # delete 
  def delete(self):
    self.__type = 'del'
    self.__buildStatement()
    self.__execute()
  
  # vacuum 
  def vacuum(self):
    conn = Connection()
    q = 'VACUUM'
    conn.cursor.execute(q)
    del conn