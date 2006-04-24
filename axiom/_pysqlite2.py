# -*- test-case-name: axiom.test -*-

"""
PySQLite2 Connection and Cursor wrappers.

These provide a uniform interface on top of PySQLite2 for Axiom, particularly
including error handling behavior and exception types.
"""
import time

from pysqlite2 import dbapi2

from twisted.python import log

from axiom import errors, iaxiom

class Connection(object):
    def __init__(self, dbfname, timeout=10.0, isolationLevel=None):
        self._connection = dbapi2.connect(dbfname,
                                          timeout=0,
                                          isolation_level=isolationLevel)
        self._timeout = timeout


    def cursor(self):
        return Cursor(self, self._timeout)



class Cursor(object):
    def __init__(self, connection, timeout):
        self._connection = connection
        self._cursor = connection._connection.cursor()
        self.timeout = timeout


    def __iter__(self):
        return iter(self._cursor)


    def execute(self, sql, args=()):
        try:
            try:
                t = time.time()
                try:
                    # SQLite3 uses something like exponential backoff when
                    # trying to acquire a database lock.  This means that even
                    # for very long timeouts, it may only attempt to acquire
                    # the lock a handful of times.  Another process which is
                    # executing frequent, short-lived transactions may acquire
                    # and release the lock many times between any two attempts
                    # by this one to acquire it.  If this process gets unlucky
                    # just a few times, this execute may fail to acquire the
                    # lock within the specified timeout.

                    # Since attempting to acquire the lock is a fairly cheap
                    # operation, we take another route.  SQLite3 is always told
                    # to use a timeout of 0 - ie, acquire it on the first try
                    # or fail instantly.  We will keep doing this, ten times a
                    # second, until the actual timeout expires.

                    # What would be really fantastic is a notification
                    # mechanism for information about the state of the lock
                    # changing.  Of course this clearly insane, no one has ever
                    # managed to invent a tool for communicating one bit of
                    # information between multiple processes.
                    while 1:
                        try:
                            return self._cursor.execute(sql, args)
                        except dbapi2.OperationalError, e:
                            if e.args[0] == 'database is locked':
                                now = time.time()
                                if now - t > self.timeout:
                                    raise
                                time.sleep(0.1)
                            else:
                                raise
                finally:
                    log.msg(interface=iaxiom.IStatEvent,
                            stat_cursor_execute_time=time.time() - t)
            except dbapi2.OperationalError, e:
                if e.args[0] == 'database schema has changed':
                    return self._cursor.execute(sql, args)
                raise
        except (dbapi2.ProgrammingError,
                dbapi2.InterfaceError,
                dbapi2.OperationalError), e:
            raise errors.SQLError(sql, args, e)


    def lastRowID(self):
        return self._cursor.lastrowid


    def close(self):
        self._cursor.close()