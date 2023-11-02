import mysql.connector
from datetime import datetime
 
month = datetime.now().month
year = datetime.now().year
day = datetime.now().day


"""
Create a function in order to apply DRY principle for this script
"""

def status():
  mydb = mysql.connector.connect(
  host="192.168.0.13",
  user="looker",
  password="looker@23#",
  database="asterisk"
  )
  mycursor = mydb.cursor(buffered=True)

  mycursor.execute(f"""
                   SELECT status FROM vicidial_log WHERE 
                    EXTRACT(YEAR FROM call_date) = {year}  
                    AND EXTRACT(MONTH FROM call_date) = {month} 
                    AND EXTRACT(DAY FROM call_date) = {day} ORDER BY call_date DESC
                    """)

  myresult = mycursor.fetchone()


  return myresult[0]

def calls():
  mydb = mysql.connector.connect(
  host="192.168.0.13",
  user="looker",
  password="looker@23#",
  database="asterisk"
  )
  mycursor = mydb.cursor(buffered=True)
  query = f"""
  SELECT SUM(called_count) FROM vicidial_log 
  WHERE user=211249 AND EXTRACT(YEAR FROM call_date) = {year} 
  AND EXTRACT(MONTH FROM call_date) = {month} AND EXTRACT(DAY FROM call_date) = {day};
  """
  mycursor.execute(query)
  myresult = mycursor.fetchone()
  return myresult[0]


def agent_list():
  mydb = mysql.connector.connect(
  host="192.168.0.13",
  user="looker",
  password="looker@23#",
  database="asterisk"
  )
  listQuewry = "SELECT `user`, full_name FROM vicidial_users"
  mycursor = mydb.cursor()
  mycursor.execute(listQuewry)
  myresult = mycursor.fetchall()
  return myresult


def agentInfo(id):
  mydb = mysql.connector.connect(
  host="192.168.0.13",
  user="looker",
  password="looker@23#",
  database="asterisk"
  )
  mycursor = mydb.cursor()

  mycursor.execute(f"""
                   SELECT * FROM vicidial_log WHERE user = '{id}'
                    AND EXTRACT(YEAR FROM call_date) = {year}  
                    AND EXTRACT(MONTH FROM call_date) = {month} 
                    AND EXTRACT(DAY FROM call_date) = {day} ORDER BY call_date DESC LIMIT 10
                    """)

  myresult = mycursor.fetchall()
  return myresult

