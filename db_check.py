#this function just adds a record to the database of threadID's
def create_record(c, conn, threadId, date, sender):
    c.execute("INSERT INTO sent_emails (threadId, emailDate, postUser) VALUES (?,?,?)", (threadId,date,sender))
    conn.commit()


# check if the email thread has alreaby been processed
def check_duplicate(c, msg):
    threadID = msg['threadId']
    c.execute('SELECT 1 from sent_emails where threadId = ?', (threadID,))
    if c.fetchone():
        return 1 #return 1 if this is a duplicate
    else:
        return 0 #return 0 if this is a new lead
