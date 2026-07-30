# ---------------- core/db_client.py ----------------
import oracledb

class DBClientISL:
    def __init__(self, dsn):

        self.dsn = dsn
        self.pool = None
        self.connected = False
    
    def create_pool(self, user, password):
        try:
            self.pool = self.get_pool(user, password)
            with self.pool.acquire() as conn:
                conn.ping()
            self.connected = True
        except Exception as e:
            self.pool = None
            self.connected = False
            raise e

    def get_pool(self, user, password):
        pool = oracledb.create_pool(
            user=user,
            password=password,
            dsn=self.dsn,
            min=2,
            max=10,
            increment=1,
            timeout=60
        )
        return pool
    
    def get_conn(self):
        conn = self.pool.acquire()
        conn.autocommit = False
        return conn
    
    def execute_conn_select(self, conn, sql, bind_vars = None):
        with conn.cursor() as cursor:
            if bind_vars:
                cursor.execute(sql, bind_vars)
            else:
                cursor.execute(sql)
            cols = [col[0] for col in cursor.description]
            return [dict(zip(cols,row)) for row in cursor.fetchall()]

    def execute_conn_dml(self, conn, sql, bind_vars = None): 
        with conn.cursor() as cursor:
            cursor.execute(sql, bind_vars)
            return cursor.rowcount
            
    def commit_conn(self, conn):
        conn.commit()

    def rollback_conn(self, conn):        
        conn.rollback()    


