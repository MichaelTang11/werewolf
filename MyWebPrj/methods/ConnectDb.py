import sqlite3

conn = sqlite3.connect("werewolf.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS room (
      id INT PRIMARY KEY NOT NULL,
      player_num INT NOT NULL
    )""")
conn.commit()







#import pymysql

#con = pymysql.connect(host='localhost',user='root',password='usbw',port='3306',database='werewolf',charset='utf8')

#cursor=con.cursor()
