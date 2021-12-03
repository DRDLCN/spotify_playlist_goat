from website import mysql,app
from flaskext.mysql import MySQL
import logging
from pymysql.cursors import DictCursor

def insert(query,tuple,id=False):
  try:
    connection = mysql.connect()
    cursor = connection.cursor()
    cursor.execute(query,tuple)
    connection.commit()
    id_ = cursor.lastrowid
    cursor.close()
    connection.close()
    if id:
      return id_
    else:
      return True
  except Exception as e:
    app.logger.debug("Problem inserting into db: " + str(e))
    cursor.close()
    connection.close()
    return False

def update(query,tuple):
  try:
    connection = mysql.connect()
    cursor = connection.cursor()
    cursor.execute(query,tuple)
    n = cursor.rowcount
    connection.commit()
    cursor.close()
    connection.close()
    return n
  except Exception as e:
    app.logger.debug("Problem updating into db: " + str(e))
    cursor.close()
    connection.close()
    return 0

def select(query,tuple,n=-1):
  try:
    connection = mysql.connect()
    cursor = connection.cursor(cursor=DictCursor)
    cursor.execute(query,tuple)
    data = None
    if n == -1:
      data = cursor.fetchall()
    elif n == 1:
      data = cursor.fetchone()
      if data == None:
        data = False
    else:
      data = cursor.fetchmany(n)
    cursor.close()
    connection.close()
    return data
  except Exception as e:
    app.logger.debug("Problem selecting into db: " + str(e))
    cursor.close()
    connection.close()
    return False