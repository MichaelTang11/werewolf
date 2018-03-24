import pymysql

con = pymysql.connect(host='localhost',user='root',password='usbw',port='3306',database='werewolf',charset='utf8')

cursor=con.cursor()