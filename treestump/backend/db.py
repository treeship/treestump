import psycopg2
import sys
import os
sys.path.append( os.path.join(os.path.dirname(__file__), '..') )
from settings import *


def connect(dbname):
    try:
        connection = "dbname='%s' user='%s' port='%d'" % (dbname, DBUSER, DBPORT)
        db = psycopg2.connect(connection)
    except:
        sys.stderr.write( "couldn't connect\n")
        sys.exit()
    return db

def prepare(db, queryline, params = None, bexit=True, commit=True):
    #print queryline
    if db == None: return ()
    try:
        cur = db.cursor()
        if params:
            cur.execute(queryline, params)
        else:
            cur.execute(queryline)
        ret = None
        for row in cur:
            ret = row
        if commit:
            db.commit()
        cur.close()            
        return ret
    except:
        db.rollback()
        print >>sys.stderr, "DBError: %s" % sys.exc_info() 
        #print >>sys.stderr, "DBError: %s\t%s" % ( queryline, sys.exc_info() )
        if bexit:
            sys.exit()
    return None

def query(db, queryline, params=None):
    if db == None: return
    try:
        cur = db.cursor()
        if params:
            cur.execute(queryline, params)
        else:
            cur.execute(queryline)
        try:
            for row in cur:
                yield row
            #result = cur.fetchall()
        except Exception as e:
            print e
            result = []
        cur.close()
    except:
        sys.stderr.write( "DBError: %s\t%s\n" % (queryline, sys.exc_info()))
        result = []
        #sys.exit()
    #return result

def close(db):
    if db != None:
        db.close()

def vacuum(db):
    if db == None: return
    isolation = db.isolation_level
    db.set_isolation_level(0)
    prepare(db, 'vacuum;', False)
    prepare(db, 'analyze;', False)
    db.set_isolation_level(isolation)


def rename(conn, oldname, newname):
    prepare(conn, 'ALTER TABLE %s RENAME TO %s;' % (oldname, newname), False)


def addindex(conn, table, attrs, where=None, name=None):
    if conn == None: return
    if name == None:
        name = ("idx_%s_%s" % (table, "_".join(attrs))).lower()
    if where is None:
        where = ""
    else:
        where = "where %s" % where
        
    q = "CREATE INDEX %s ON %s (%s) %s;" % (
        name, table, ",".join(attrs), where)
    prepare(conn, q, False)


def clusterindex(conn, table, attrs):
    if conn == None: return
    name = ("idx_%s_%s" % (table, "_".join(attrs))).lower()
    tmptable = "tmp_%s" % table
    create = "CREATE TABLE %s AS SELECT * from %s ORDER BY %s;" % (tmptable, table, ' , '.join(attrs))
    drop = "DROP TABLE %s;" % table
    alter = "ALTER TABLE %s RENAME TO %s;" % (tmptable, table)
    cluster = "CLUSTER %s ON %s;" % (name, table)

    prepare(conn, "DROP TABLE %s;" % tmptable, False)
    prepare(conn, create, False)
    prepare(conn, drop, False)
    prepare(conn, alter, False)
    addindex(conn, table, attrs)
    prepare(conn, cluster, False)
    

def dropindex(conn, table, attrs, name=None):
    if conn == None: return    
    if name == None: name = ("idx_%s_%s" % (table, "_".join(attrs))).lower()
    prepare(conn, "DROP INDEX %s;" % name, False)

def indexexists(conn, table, attrs, name=None):
    if conn == None: return False
    if name == None: name = ("idx_%s_%s" % (table, "_".join(attrs))).lower()
    q = "select * from pg_indexes where indexname = '%s';" % name
    return len(query(conn, q)) > 0

def indexsize(conn, table, attrs, name=None):
    if conn == None: return 0
    if name == None:
        name = ("idx_%s_%s" % (table, "_".join(attrs))).lower()
    q = """select pg_total_relation_size(indexname::text)
    from pg_indexes where schemaname != 'pg_catalog' and schemaname != 'information_schema' and indexname='%s';""" % name
    v = query(conn, q)[0][0]
    if v == None: return 0
    return int(v)


def indexsizes(conn):
    if conn == None: return 0
    q = """select sum(pg_total_relation_size(indexname::text))
    from pg_indexes where schemaname != 'pg_catalog' and schemaname != 'information_schema';"""
    v = query(conn, q)[0][0]
    if v == None: return 0
    return int(v)

def tablesize(conn, tablename):
    if conn == None: return 0
    sizes = tablesizes(conn)
    if tablename not in sizes: return 0
    return sizes[tablename]

def tablesizes(conn):
    if conn == None: return {'data' : 0}    
    q = """select tablename, pg_total_relation_size(tablename::text)
    from pg_tables where schemaname != 'pg_catalog' and schemaname != 'information_schema';"""
    ress = query(conn, q)

    ret = {}
    for res in ress:
        ret[res[0]] = res[1]
    return ret


def cleandatabase(db):
    if db == None: return
    isolation = db.isolation_level
    db.set_isolation_level(0)
    q = "select tablename from pg_tables where schemaname='public' and tablename != 'data';"
    tablenames = query(db, q)
    for tablename in tablenames:
        d = "drop table %s;" % tablename
        prepare(db, d, False)
    
    q = "select indexname from pg_indexes where schemaname='public';"
    indexnames = query(db, q)
    for indexname in indexnames:
        d = "drop index %s;" % indexname
        prepare(db, d, False)

    #prepare(db, 'delete from data where id < 0;', False)
    
    db.set_isolation_level(isolation)
