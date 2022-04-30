#
# Introducing MySQL InnoDB Cluster
#
# This file contains classes that implement a relational database model
# for the Shopping List application. Included are the basic create, read,
# update, and delete methods for lists. 
#
# Additional functions are provided for connecting to and disconnecting
# from the MySQL server.
#
# Database name = shopping
#
# Dr. Charles Bell, 2018
#
import mysql.connector
import time

RW_PORT = 6446
RO_PORT = 6447
MAX_RETRY = 6  # Maximum times to attempt a reconnect should connection fail

#
# String SQL Statements
#
ALL_ITEMS = """
    SELECT * FROM shopping.list
    ORDER BY description
"""

READ_ITEM = """
    SELECT * FROM shopping.list
    WHERE rowid = '{0}'
"""

UNCHECKED_ITEMS = """
    SELECT * FROM shopping.list
    WHERE purchased = 0
    ORDER BY description
"""

INSERT_ITEM = """
    INSERT INTO shopping.list (description, note) VALUES ('{0}','{1}')
"""

GET_LASTID = "SELECT @@last_insert_id"

UPDATE_ITEM = """
    UPDATE shopping.list
    SET description = '{1}', note = '{2}'
    WHERE rowid = '{0}'
"""

UPDATE_PURCHASED = """
    UPDATE shopping.list
    SET purchased = {1}
    WHERE rowid = '{0}'
"""

DELETE_ITEM = """
    DELETE FROM shopping.list WHERE rowid = '{0}'
"""

#
# List table simple abstraction (relational database)
#
class ShoppingList(object):
    """ShoppingList class
    
    This class encapsulates the list table permitting CRUD operations
    on the data.
    """
    def __init__(self, library):
        self.library = library

    def create(self, description, note):
        assert description, "You must supply a description for a new item."
        self.library.connect(True)
        query_str = INSERT_ITEM
        last_id = None
        try:
            self.library.sql(query_str.format(description, note))
            last_id = self.library.sql(GET_LASTID)
            self.library.sql("COMMIT")
        except Exception as err:
            print("ERROR: Cannot add item: {0}".format(err))
        self.library.disconnect()
        return last_id
    
    def read(self, rowid):
        assert rowid, "You must supply a rowid."
        self.library.connect()
        query_str = READ_ITEM.format(rowid)
        results = self.library.sql(query_str)            
        self.library.disconnect()
        return results            
        
    def update(self, rowid, description, note):
        assert rowid, "You must supply a rowid."
        assert description, "You must supply a description for a new item."
        self.library.connect(True)
        query_str = UPDATE_ITEM
        try:
            self.library.sql(query_str.format(rowid, description, note))
            self.library.sql("COMMIT")
        except Exception as err:
            print("ERROR: Cannot update list item: {0}".format(err))
        self.library.disconnect()

    def update_purchased(self, rowid, Purchased=1):
        assert rowid, "You must supply a rowid."
        self.library.connect(True)
        query_str = UPDATE_PURCHASED
        try:
            self.library.sql(query_str.format(rowid, Purchased))
            self.library.sql("COMMIT")
        except Exception as err:
            print("ERROR: Cannot update list item: {0}".format(err))
        self.library.disconnect()
    
    def delete(self, rowid):
        assert rowid, "You must supply a rowid."
        self.library.connect(True)
        query_str = DELETE_ITEM.format(rowid)
        try:
            self.library.sql(query_str)
            self.library.sql("COMMIT")
        except Exception as err:
            print("ERROR: Cannot delete item: {0}".format(err))
        self.library.disconnect()
    
#
# Library database simple abstraction (relational database)
#
class Library(object):
    """Library master class
    
    Use this class to interface with the library database. It includes
    utility functions for connections to the server as well as running
    queries.
    """
    def __init__(self):
        self.config = {
            'user': 'root',
            'password': 'root',
            'host': 'mysql-router',
            'port': RO_PORT,
            'database': None,
        }
        self.db_conn = None
    
    #
    # Connect to a MySQL server at host, port
    #
    # Attempts to connect to the server as specified by the connection
    # parameters.
    # 
    def connect(self, read_write=False):
        attempts = 0
        while attempts < MAX_RETRY:
            self.config['port'] = (RO_PORT, RW_PORT)[read_write]
            try:
                self.db_conn = mysql.connector.connect(**self.config)
                break
            except mysql.connector.Error as err:
                print("Connection failed. Error = {0} Retrying.".format(err))
            attempts += 1
            time.sleep(1)
        if attempts >= MAX_RETRY:
           self.db_conn = None
           raise mysql.connector.Error("Connection timeout reached.")
            
    #
    # Return the connection for use in other classes
    #
    def get_connection(self):
        return self.db_conn
    
    #
    # Check to see if connected to the server
    #
    def is_connected(self):
        return (self.db_conn and (self.db_conn.is_connected()))
    
    #
    # Disconnect from the server
    #
    def disconnect(self):
        try:
            self.db_conn.disconnect()
        except:
            pass

    #
    # Execute a query and return any results
    #
    # query_str[in]      The query to execute
    # fetch          Execute the fetch as part of the operation and
    #                use a buffered cursor (default is True)
    # buffered       If True, use a buffered raw cursor (default is False)
    #
    # Returns result set or cursor
    # 
    def sql(self, query_str, fetch=True, buffered=False):
        # If we are fetching all, we need to use a buffered
        if fetch:
            cur = self.db_conn.cursor(buffered=True)
        else:
            cur = self.db_conn.cursor(raw=True)

        try:
            cur.execute(query_str)
        except Exception as err:
            cur.close()
            print("Query error. Command: {0}:{1}".format(query_str, err))
            raise

        # Fetch rows (only if available or fetch = True).
        if cur.with_rows:
            if fetch:
                try:
                    results = cur.fetchall()
                except mysql.connector.Error as err:
                    print("Error fetching all query data: {0}".format(err))
                    raise
                finally:
                    cur.close()
                return results
            else:
                # Return cursor to fetch rows elsewhere (fetch = false).
                return cur
        else:
            return cur

    #
    # Get list of items
    #
    def get_list(self, all=True):
        self.connect()
        try:
            if all:
                results = self.sql(ALL_ITEMS)
            else:
                results = self.sql(UNCHECKED_ITEMS)
        except Exception as err:
            print("ERROR: {0}".format(err))
            raise
        self.disconnect()
        return results
    
