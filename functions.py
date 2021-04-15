
def dbSelectCallEsc(mysql, query, data):
    cur = mysql.connection.cursor()
    cur.execute(query, data)
    dbresponse = cur.fetchall()
    cur.close()
    return dbresponse


def dbSelectCall(mysql, query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    dbresponse = cur.fetchall()
    cur.close()
    return dbresponse