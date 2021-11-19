import vddb_postgresql as vddb

if vddb.initConnection():
    vddb.utCreateRecords()
    vddb.closeConnection()

