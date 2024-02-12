# this contain files for accessing db and 
# related utilities
import sqlite3,os

def checkLogin(username,password):
    """ check the supplied username and password in sqlite
        before authorizing access
    """
    # terminate early if file dont exists
    if os.path.exists("users.sqlite"): return False
    
    db  = sqlite3.connect("users.sqlite")
    # create cursor to execute query
    cursor = db.cursor()
    cursor.execute("select from users where username = ? && password = ?",[username,password])
    if cursor.rowcount:
        return True
    else return False


# this initialize users database
def initDatabase(file):
    """ create our users database"""
    connect = sqlite3.connect(file,"c")
    # create cursor
    cursor = connect.cursor()
    # create our users table
    stm = """create table users(
      id int primary key, username char(50), password char(50)
    )"""
    # create our users table
    cursor.execute(stm)
