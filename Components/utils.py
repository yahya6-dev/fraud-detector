# this contain files for accessing db and 
# related utilities
import sqlite3,os
import pygame

def checkLogin(username,password):
    """ check the supplied username and password in sqlite
        before authorizing access
    """
    # terminate early if file dont exists
    if not os.path.exists("./Components/users.sqlite"):
        print("terminate early")
        return False
    
    db  = sqlite3.connect("./Components/users.sqlite")
    # create cursor to execute query
    cursor = db.cursor()
    cursor.execute("select username,password from users where username = ? and password = ?",[username,password])
    # details
    details = cursor.fetchone()
    print(details,"from utils")
    if details:
        return True
    else: return False


# this initialize users database
def initDatabase(file):
    """ create our users database"""
    connect = sqlite3.connect(file)
    # create cursor
    cursor = connect.cursor()
    # create our users table
    stm = """create table users(
      id int unsigned  auto_increment, username char(50), password char(50),
      primary key(id)
    )"""
    # create our users table
    cursor.execute(stm)
    # insert a user into our database
    stm_user_create = "insert into users(username,password)  values('admin','admin')"
    cursor.execute(stm_user_create)
    # create our trial table
    stm_crt_trial_table = """create table trial(id int auto_increment,
        days int default 0, istrial int default 0, primary key(id)
    )"""
    cursor.execute(stm_crt_trial_table)
    connect.commit()

# return information on trials day 
def getTrialInfo(filename="./Components/users.sqlite"):
    conn = sqlite3.connect(filename)
    # get  db connection
    cursor = conn.cursor()
    # read our trial table
    cursor.execute("select istrial,days from trial")
    return cursor,conn,cursor.fetchone()


def playSound(filename):
    pygame.mixer.init()
    pygame.mixer.Sound(filename).play()