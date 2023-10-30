import mysql.connector
from datetime import datetime
 
month = datetime.now().month
year = datetime.now().year
day = datetime.now().day

mydb = mysql.connector.connect(
  host="192.168.0.13",
  user="looker",
  password="looker@23#",
  database="asterisk"
)

def status():
  mycursor = mydb.cursor(buffered=True)

  mycursor.execute(f"""
                   SELECT status FROM vicidial_log WHERE 
                    EXTRACT(YEAR FROM call_date) = {year}  
                    AND EXTRACT(MONTH FROM call_date) = {month} 
                    AND EXTRACT(DAY FROM call_date) = {day} ORDER BY call_date DESC LIMIT 10
                    """)

  myresult = mycursor.fetchone()


  return myresult[0]

def calls():
  mycursor = mydb.cursor()
  query = f"""
  SELECT SUM(called_count) FROM vicidial_log 
  WHERE user=211249 AND EXTRACT(YEAR FROM call_date) = {year} 
  AND EXTRACT(MONTH FROM call_date) = {month} AND EXTRACT(DAY FROM call_date) = {day};
  """
  mycursor.execute(query)
  myresult = mycursor.fetchone()
  return myresult[0]


def agent_list():
  listQuewry = "SELECT `user`, full_name FROM vicidial_users"
  mycursor = mydb.cursor(buffered=True)
  mycursor.execute(listQuewry)
  myresult = mycursor.fetchall()
  return myresult


