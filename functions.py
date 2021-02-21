
def dbSelectCall(mysql, query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    dbresponse = cur.fetchall()
    cur.close()
    return dbresponse