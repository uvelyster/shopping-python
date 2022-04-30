import mysql.connector
conn_dict = {
'user':'root',
'passwd':'<secret>',
'port':6446,
'host':'cluster-rpi-app',
}
conn = mysql.connector.connect(**conn_dict)
cur = conn.cursor()
res = cur.execute("SHOW DATABASES")
for row in cur:
  print(row)
cur.close()
conn.close()

