from ..helpers import config, db, migrate, timestamp
import collections

def depInjector(name):
  from ..models._index import registry
  return registry[name]
    
def keyOfDep(dep):
  from ..models._index import registry
  for r in registry.items():
    if r[1] == dep:
      return r[0]

class Model:
  connection = config.get(f'db.list.{config.get("db.current")}')
  softDeletes = False 
  timestamps = True 
  relations = {}
  touch = []
  schema = migrate.schema(False, connection)
  
  def __init__(self, values = None):
    self.__originals = {}
    self.__lastPushed = {}
    self.__lastPulled = {}
    self.__includeTrashed = False
    self.__onlyTrashed = False 
    self.__distinct = False
    self.__limit = None 
    self.__ordering = []
    self.__conditions = None
    self.__loadedRelations = []
    self.__record = {}
    for c in self.__class__.schema[self.__class__.table].keys():
      self.__record[c] = None
    if values != None:
      for k in values.keys():
        self[k] = values[k]
        self.__originals[k] = values[k]

  def __getitem__(self, key):
    return self.__record[key]

  def isSameModel(self, other):
    res = False 
    if self['id'] == other['id'] and self.__class__.table == other.__class__.table and self.__class__.connection == other.__class__.connection:
      res = True
    return res

  def isNotSameModel(self, other):
    return not(self.isSameModel(other))

  def __setitem__(self, key, newval):
    self.__record[key] = newval

  def setOriginals(self, cols):
    self.__originals = {}
    for c in cols.keys():
      self.__originals[c] = cols[c]
    
  def getOriginal(self):
    return self.__originals 
    
  def hydrated(self):
    res = True 
    for k in self.__class__.schema[self.__class__.table].keys():
      if not(self.__class__.schema[self.__class__.table][k]['nullable']) and self.__record[k] == None:
        res = False
        break
    return res

  def __processTrashCondition(self, relation = None):
    if relation == None and self.__class__.softDeletes:
      tc = {'type':'single'}
      
      if self.__onlyTrashed:
        tc['condition'] = ('deleted_at', 'IS NOT', None)
      elif not(self.__includeTrashed):
        tc['condition'] = ('deleted_at', 'IS', None)
      else:
      	tc['condition'] = None
        
      if self.__conditions != None:
        if tc['condition'] != None:
          self.__conditions.prependCondition(tc)
      else:
        if tc['condition'] != None:
          self.__conditions = db.Where([tc,])
      if self.__conditions != None:
        self.__conditions.parse()
    elif relation != None and relation.softDeletes:
      tc = {'type':'single'}
      
      if self.__onlyTrashed:
        tc['condition'] = ('deleted_at', 'IS NOT', None)
      elif not(self.__includeTrashed):
        tc['condition'] = ('deleted_at', 'IS', None)
      else:
      	tc['condition'] = None
        
      if self.__conditions != None:
        if tc['condition'] != None:
          self.__conditions.prependCondition(tc)
      else:
        if tc['condition'] != None:
          self.__conditions = db.Where([tc,])
      if self.__conditions != None:
        self.__conditions.parse()
          
  def trashed(self):
    if not(self.softDeletes) or 'deleted_at' not in self.schema[self.__class__.table].keys() or self['deleted_at'] == None:
      return False
    else:
      return True

  def withTrashed(self):
    self.__includeTrashed = True
    return self
    
  def onlyTrashed(self):
    self.__onlyTrashed = True
    return self
    
  def allModels(self):
    res = None
    self.__processTrashCondition()
    res = db.Table(self.__class__.table).setConnection(self.__class__.connection)
    if self.__conditions != None:
    	res = res.conditions(self.__conditions)
    res = res.get()
    out = []
    for r in res:
      m = self.__class__(r)
      m.setLastPulled(r)
      out.append(m)
      del m 
    return out 
    
  def fresh(self):
    res = db.Table(self.__class__.table).setConnection(self.__class__.connection).find(self['id'])
    for c in res[0].keys():
      self[c] = res[0][c]
      
  def refresh(self):
    self.fresh()
    for r in self.__loadedRelations:
      self.load(r, False)

  def find(self, id):
    self.__processTrashCondition()
    res = db.Table(self.__class__.table).setConnection(self.__class__.connection)
    if self.__conditions != None:
      res = res.conditions(self.__conditions)
    res = res.find(id)
    if len(res) > 0:
      m = self.__class__(res[0])
      m.setLastPulled(res[0])
      return m
    else:
      return None
  
  def setLastPulled(self,record):
    for k in record.keys():
      self.__lastPulled[k] = record[k]

  def save(self):
    if self['id'] != None:
      # update
      if self.__class__.timestamps:
        self['updated_at'] = timestamp.getNixTs()
        self.__lastPushed['updated_at'] = self['updated_at']
      cols = []
      vals = []
      for k in self.__record.keys():
        self.__lastPushed[k] = self.__record[k]
        self.__lastPulled[k] = self.__record[k]
        cols.append(k)
        vals.append(self.__record[k])
      # update record 
      db.Table(self.__class__.table).setConnection(self.__class__.connection).condition('id','=',self['id']).update(cols,vals)
      self.__touchIfNeeded()
    else:
      # create
      if self.__class__.timestamps:
        self['created_at'] = timestamp.getNixTs()
        self.__lastPushed['created_at'] = self['created_at']
      # update lastPushed dict
      cols = []
      vals = []
      for k in self.__record.keys():
        self.__lastPushed[k] = self.__record[k]
        self.__lastPulled[k] = self.__record[k]
        cols.append(k)
        vals.append(self.__record[k])
      # push record 
      newid = db.Table(self.__class__.table).setConnection(self.__class__.connection).insertGetId(cols,[vals])
      self['id'] = newid 
      self.setOriginals(self.__record)
      self.__lastPushed['id'] = newid
  
  def limit(self,l):
    self.__limit = l
    return self 
    
  def orderBy(self,col,d = 'asc'):
    self.__ordering.append((col,d))
    return self
    
  def condition(self, col, op, val):
    self.__conditions = db.Where([{'type':'single','condition':(col,op,val)}])
    return self
    
  def conditions(self, ws):
    self.__conditions = ws
    return self
    
  def get(self):
    q = db.Table(self.__class__.table).setConnection(self.__class__.connection)
    if self.__distinct:
      q = q.distinct()
    self.__processTrashCondition()
    if self.__conditions != None:
      q = q.conditions(self.__conditions)
    if self.__limit != None:
      q = q.limit(self.__limit)
    if len(self.__ordering) > 0:
      for o in self.__ordering:
        q = q.orderBy(o[0],o[1])
    raw = q.get()
    res = []
    for r in raw:
      m = self.__class__(r)
      m.setLastPulled(r)
      res.append(m)
    return res

  def chunk(self, size, cb):
    statement = f'SELECT * FROM {self.__class__.table}'
    limit = size
    offset = 0
    params = [] 
    self.__processTrashCondition()
    statement += ' '
    if self.__conditions != None:
      statement += self.__conditions.getConditionString()
      for p in self.__conditions.getParams():
        params.append(p)
    statement += ' LIMIT ?'
    params.append(limit)
    statement += ' OFFSET ?'
    params.append(offset)
    conn = db.Connection(True, self.__class__.connection)
    cur = conn.cursor
    res = cur.execute(statement, params).fetchall()
    del conn
    discontinue = False
    for rec in res:
      m = self.__class__(rec)
      m.setLastPulled(rec)
      if not cb(m):
        discontinue = True
    while len(res) > 0 and not(discontinue):
      offset += size
      statement = f'SELECT * FROM {self.__class__.table}'
      params = []
      statement += ' '
      if self.__conditions != None:
        self.__conditions.parse()
        statement += self.__conditions.getConditionString()
        for p in self.__conditions.getParams():
          params.append(p)
      statement += ' LIMIT ?'
      params.append(limit)
      statement += ' OFFSET ?'
      params.append(offset)
      conn = db.Connection(True, self.__class__.connection)
      cur = conn.cursor
      res = cur.execute(statement, params).fetchall()
      del conn
      for rec in res:
        m = self.__class__(rec)
        m.setLastPulled(rec)
        if not cb(m):
          discontinue = True
          break
  
  def chunkById(self, size, cb):
    statement = f'SELECT * FROM {self.__class__.table}'
    limit = size
    last = 0
    if self.__conditions == None:
      self.__conditions = db.Where([])
    self.__conditions.prependCondition({'type':'single','condition':('id','>',last)})
    self.__conditions.parse()
    params = []
    statement += ' '
    statement += self.__conditions.getConditionString()
    for p in self.__conditions.getParams():
      params.append(p)
    statement += ' ORDER BY id LIMIT ?'
    params.append(limit)
    conn = db.Connection(True, self.__class__.connection)
    cur = conn.cursor
    res = cur.execute(statement, params).fetchall()
    del conn
    discontinue = False
    for rec in res:
      last = rec['id']
      m = self.__class__(rec)
      m.setLastPulled(rec)
      if not cb(m):
        discontinue = True
    while len(res) > 0 and not(discontinue):
      self.__conditions.setCondition(0,{'type':'single','condition':('id','>',last)})
      self.__conditions.parse()
      statement = f'SELECT * FROM {self.__class__.table}'
      params = []
      statement += ' '
      statement += self.__conditions.getConditionString()
      for p in self.__conditions.getParams():
        params.append(p)
      statement += ' ORDER BY id LIMIT ?'
      params.append(limit)
      conn = db.Connection(True, self.__class__.connection)
      cur = conn.cursor
      res = cur.execute(statement, params).fetchall()
      del conn
      for rec in res:
        last = rec['id']
        m = self.__class__(rec)
        m.setLastPulled(rec)
        if not cb(m):
          discontinue = True
          break
  
  def delete(self):
    if self.softDeletes:
      db.Table(self.__class__.table).setConnection(self.__class__.connection).condition('id', '=', self['id']).update(['deleted_at'], [timestamp.getNixTs()])
    else:
      q = db.Table(self.__class__.table).setConnection(self.__class__.connection)
      if self.__conditions!= None:
        q = q.conditions(self.__conditions)
      else:
        q = q.condition('id', '=', self['id'])
      q.delete()
    self.__touchIfNeeded()
  
  def forceDelete(self):
    q = db.Table(self.__class__.table).setConnection(self.__class__.connection)
    if self.__conditions!= None:
      q = q.conditions(self.__conditions)
    else:
      q = q.condition('id', '=', self['id'])
    q.delete()
    self.__touchIfNeeded()
  
  def destroy(self, targetId):
    if self.softDeletes:
      db.Table(self.__class__.table).setConnection(self.__class__.connection).condition('id', '=', targetId).update(['deleted_at'],[timestamp.getNixTs()])
    else:
      db.Table(self.__class__.table).setConnection(self.__class__.connection).condition('id', '=', targetId).delete()
  
  def restore(self):
    if self.__class__.softDeletes:
      db.Table(self.__class__.table).setConnection(self.__class__.connection).condition('id','=', self['id']).update(['deleted_at'],[None])
      self.__touchIfNeeded()
  
  # relation loaders 
  
  def load(self, name, updateLoaded = True):
    if name in self.__class__.relations.keys() and 'id' in self.__record.keys() and self['id'] != None:
      if self.__class__.relations[name]['type'] == 'hasOne':
          if self.__hasOne(name) and updateLoaded:
            self.__loadedRelations.append(name)
      elif self.__class__.relations[name]['type'] == 'hasMany':
          if self.__hasMany(name) and updateLoaded:
            self.__loadedRelations.append(name)
      elif self.__class__.relations[name]['type'] == 'belongsTo':
          if self.__belongsTo(name) and updateLoaded:
            self.__loadedRelations.append(name)
      elif self.__class__.relations[name]['type'] == 'belongsToMany':
          if self.__belongsToMany(name) and updateLoaded:
            self.__loadedRelations.append(name)
      elif self.__class__.relations[name]['type'] == 'morphOne':
          if self.__morphOne(name) and updateLoaded:
            self.__loadedRelations.append(name)
      elif self.__class__.relations[name]['type'] == 'morphTo':
          if self.__morphTo(name) and updateLoaded:
            self.__loadedRelations.append(name)
      elif self.__class__.relations[name]['type'] == 'morphMany':
          if self.__morphMany(name) and updateLoaded:
            self.__loadedRelations.append(name)
      elif self.__class__.relations[name]['type'] == 'morphToMany':
          if self.__morphToMany(name) and updateLoaded:
            self.__loadedRelations.append(name)
      elif self.__class__.relations[name]['type'] == 'morphedByMany':
          if self.__morphedByMany(name) and updateLoaded:
            self.__loadedRelations.append(name)
  
  def __hasOne(self, name):
    r = self.__class__.relations[name]
    model = depInjector(r['model'])
    foreign = self.__class__.table + '_id'
    if 'foreign' in r.keys():
      foreign = r['foreign']
    self.__conditions = db.Where([{'type':'single','condition':(foreign,'=',self['id'])}])
    self.__processTrashCondition(model)
    q = db.Table(model.table).setConnection(model.connection).limit(1).conditions(self.__conditions)
    if len(self.__ordering) > 0:
      for o in self.__ordering:
        q = q.orderBy(o[0],o[1])
    res = q.get()
    loaded = False
    if len(res) < 1:
      if 'default' in r.keys():
        m = model(r['default'])
        m.setOriginals(r['default'])
        self[name] = m
      else: 
        self[name] = None 
    else:
      loaded = True
      m = model(res[0])
      m.setOriginals(res[0])
      self[name] = m
    return loaded
  
  def __hasMany(self, name):
    r = self.__class__.relations[name]
    model = depInjector(r['model'])
    foreign = self.__class__.table + '_id'
    if 'foreign' in r.keys():
      foreign = r['foreign']
    self.__conditions = db.Where([{'type':'single','condition':(foreign,'=',self['id'])}])
    self.__processTrashCondition(model)
    q = db.Table(model.table).setConnection(model.connection).conditions(self.__conditions)
    if self.__limit != None:
      q = q.limit(self.__limit)
    if len(self.__ordering) > 0:
      for o in self.__ordering:
        q = q.orderBy(o[0],o[1])
    res = q.get()
    loaded = False
    if len(res) < 1:
      self[name] = None 
    else:
      loaded = True
      a = []
      for r in res:
        m = model(r)
        m.setOriginals(r)
        a.append(m)
      self[name] = a 
    return loaded
  
  def __belongsTo(self, name):
    r = self.__class__.relations[name]
    model = depInjector(r['model'])
    foreign = model.table + '_id'
    if 'foreign' in r.keys():
      foreign = r['foreign']
    res = db.Table(model.table).setConnection(model.connection).limit(1).condition('id', '=', self[foreign]).get()
    loaded = False
    if len(res) < 1:
      if 'default' in r.keys():
        m = model(r['default'])
        m.setOriginals(r['default'])
        self[name] = m
      else: 
        self[name] = None 
    else:
      loaded = True
      m = model(res[0])
      m.setOriginals(res[0])
      self[name] = m
    return loaded 
  
  def __belongsToMany(self, name):
    r = self.__class__.relations[name]
    model = depInjector(r['model'])
    pivot = depInjector(r['pivot'])
    foreign = model.table + '_id'
    if 'foreign' in r.keys():
      foreign = r['foreign']
    local = self.__class__.table + '_id' 
    if 'local' in r.keys():
      local = r['local']
    mids = [r[foreign] for r in db.Table(pivot.table).setConnection(pivot.connection).columns((foreign,)).condition(local, '=', self['id']).get()]
    res = None
    if len(mids) < 1:
      res = []
    else:
      res = db.Table(model.table).setConnection(model.connection).condition('id', 'IN', mids).get()
    loaded = False
    if len(res) < 1:
      self[name] = None 
    else:
      loaded = True
      rel = []
      for r in res:
        m = model(r)
        m.setOriginals(r)
        pr = db.Table(pivot.table).setConnection(pivot.connection).conditions(db.Where([{'type':'single','condition':(foreign, '=', m['id'])},{'type':'single','operator':'AND','condition':(local, '=', self['id'])}])).first()
        p = pivot(pr[0])
        p.setOriginals(pr[0])
        m['pivot'] = p
        rel.append(m)
      self[name] = rel 
    return loaded 
  
  def __morphOne(self, name):
    r = self.__class__.relations[name]
    model = depInjector(r['model'])
    able_id = model.table + 'able_id'
    able_type = model.table + 'able_type'
    owner_string = None
    for p in model.owners:
      if p == keyOfDep(self.__class__):
        owner_string = p
        break 
    if owner_string == None:
      self[name] = None 
    else:
      c = db.Where([{'type':'series','series':[{'type':'single','condition':(able_id,'=',self['id'])},{'type':'single','operator':'AND','condition':(able_type,'=',owner_string)}]}])
      c.parse()
      res = db.Table(model.table).setConnection(model.connection).conditions(c).first()
      loaded = False
      if len(res) < 1:
        if 'default' in r.keys():
          m = model(r['default'])
          m.setOriginals(r['default'])
          self[name] = m
        else: 
          self[name] = None 
      else:
        loaded = True
        m = model(res[0])
        m.setOriginals(res[0])
        self[name] = m 
      return loaded
  
  def __morphTo(self, name):
    r = self.__class__.relations[name]
    able_id = self.__class__.table + 'able_id'
    able_type = self.__class__.table + 'able_type'
    if self[able_type] not in self.__class__.owners:
      self[name] = None 
    else:
      rt = depInjector(self[able_type])
      res = db.Table(rt.table).setConnection(rt.connection).condition('id','=',self[able_id]).first()
      loaded = False
      if len(res) < 1:
        if 'default' in r.keys():
          m = rt(r['default'])
          m.setOriginals(r['default'])
          self[name] = m
        else: 
          self[name] = None 
      else: 
        loaded = True
        m = rt(res[0])
        m.setOriginals(res[0])
        self[name] = m 
      return loaded
  
  def __morphMany(self, name):
    r = self.__class__.relations[name]
    model = depInjector(r['model'])
    able_id = model.table + 'able_id'
    able_type = model.table + 'able_type'
    owner_string = None
    for p in model.owners:
      if p == keyOfDep(self.__class__):
        owner_string = p
        break 
    if owner_string == None:
      self[name] = None 
    else:
      c = db.Where([{'type':'series','series':[{'type':'single','condition':(able_id,'=',self['id'])},{'type':'single','operator':'AND','condition':(able_type,'=',owner_string)}]}])
      c.parse()
      res = db.Table(model.table).setConnection(model.connection).conditions(c).get()
      loaded = False
      if len(res) < 1:
        self[name] = None 
      else:
        loaded = True
        rel = []
        for rec in res:
          m = model(rec)
          m.setOriginals(rec)
          rel.append(m)
        self[name] = rel 
      return loaded
  
  def __morphToMany(self, name):
    # owned 
    r = self.__class__.relations[name]
    pivot = depInjector(r['pivot'])
    foreign = self.__class__.table + '_id'
    pivs = db.Table(pivot.table).setConnection(pivot.connection).condition(foreign,'=',self['id']).get()
    loaded = False
    if len(pivs) < 1:
      self[name] = None 
    else:
      rel = []
      able_id = pivot.table + '_id'
      able_type = pivot.table + '_type'
      for p in pivs:
        if p[able_type] in pivot.morphs:
          m = depInjector(p[able_type])
          i = p[able_id]
          res = db.Table(m.table).setConnection(m.connection).condition('id','=',i).first()
          if len(res) > 0:
            o = m(res[0])
            o.setOriginals(res[0])
            rel.append(o)
      if len(rel) < 1:
        self[name] = None 
      else: 
        loaded = True
        self[name] = rel 
      return loaded
  
  def __morphedByMany(self, name):
    # owners 
    r = self.__class__.relations[name]
    model = depInjector(r['model'])
    pivot = depInjector(r['pivot'])
    owner_string = None
    for p in pivot.morphs:
      if p == keyOfDep(self.__class__):
        owner_string = p
        break 
    if owner_string == None:
      self[name] = None 
    else:
      c = db.Where([{'type':'series','series':[{'type':'single','condition':(pivot.table + '_id','=',self['id'])},{'type':'single','operator':'AND','condition':(pivot.table + '_type','=',owner_string)}]}])
      c.parse()
    mids = [k[model.table + '_id'] for k in db.Table(pivot.table).setConnection(pivot.connection).columns((model.table + '_id',)).conditions(c).get()]
    loaded = False
    if len(mids) < 1:
      self[name] = None 
    else:
      res = db.Table(model.table).setConnection(model.connection).condition('id', 'IN', mids).get()
      if len(res) < 1:
        self[name] = None 
      else:
        loaded = True
        rel = []
        for rec in res:
          m = model(rec)
          m.setOriginals(rec)
          rel.append(m)
        self[name] = rel 
      return loaded

  def __touchIfNeeded(self):
    if len(self.__class__.touch) > 0:
      for rel in self.__class__.touch:
        if rel not in self.__loadedRelations:
          self.load(rel)
        if self[rel] != None:
          if type(self[rel]) is not str and isinstance(self[rel], collections.abc.Sequence):
            for m in self[rel]:
              m['updated_at'] = timestamp.getNixTs() 
              m.save()
          else: 
            self[rel]['updated_at'] = timestamp.getNixTs()
            self[rel].save()
