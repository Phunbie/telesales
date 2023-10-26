import mysql.connector

mydb = mysql.connector.connect(
  host="192.168.0.13",
  user="looker",
  password="looker@23#",
  database="asterisk"
)

def status():
  mycursor = mydb.cursor(buffered=True)

  mycursor.execute("SELECT status  FROM vicidial_log WHERE user=211580 AND EXTRACT(YEAR FROM call_date) = 2023  AND EXTRACT(MONTH FROM call_date) = 10 AND EXTRACT(DAY FROM call_date) = 25 ORDER BY call_date DESC")

  myresult = mycursor.fetchone()


  return myresult[0]

#mycursor.execute("SELECT * FROM vicidial_log LIMIT 10")

#myresult = mycursor.fetchall()

#for x in myresult:
#  print(x[-2])