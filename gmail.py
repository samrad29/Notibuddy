import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from csv import writer
import emailSender2
import emailReader
import db_check
import time
import sqlite3


#this database is used to store the threadID of emails that triggered a notification. We will check against this database to avoid duplciate notifications
db_directory = os.path.curdir

db_path = os.path.join(db_directory, 'sent_emails.db')

conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('''
create table if not exists sent_emails (
    threadId text primary key,
    emailDate text,
    postUser text
)
''')
conn.commit()


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.modify']

# Set up credentials and create an API client
creds = None
# The file token.json stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.
# If token.json doesn't exist, we need to authenticate the user and create one
if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
# If there are no valid credentials available, you will need to log in
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'google_credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
    with open('token.json', 'w') as token:
            token.write(creds.to_json())


def check_email():
    # Call the Gmail API and fetch emails
    results = service.users().messages().list(userId= INSERT_FACEBOOK_EMAIL_HERE, q='is:unread AND from:Facebook').execute()
    messages = results.get('messages')
    i = 0
    if not messages:
        print('No messages found.')
    else:
        # If the code is here we have emails in the inbox that are unread and from Facebook
        # Note: if the email is marked as read, it will not be picked up by the code.
        for message in messages: 
            # TODO: IN THE LINE BELOW INSERT YOUR GMAIL ADDRESS THAT IS LINKED TO A FACEBOOK ACCOUNT 
            msg = service.users().messages().get(userId= 'INSERT_FACEBOOK_EMAIL_HERE' , id=message['id']).execute()
            #for each unread email from facebook we will use the emailReader.read_email(msg, service) to parse for key information (user, keywords, date, etc)
            parsed_email = emailReader.read_email(msg, service)
            i = i + 1
            try:
                #this if statement will be true if the email contains keywords
                if parsed_email.get_lead_f() >= 0:
                    uName_extracted = parsed_email.get_uName()
                    group_extracted = parsed_email.get_group()
                    preview_extracted = parsed_email.get_preview()
                    link = parsed_email.get_link()
                    date_extracted = parsed_email.get_date()
                    extract = [uName_extracted,group_extracted,date_extracted, preview_extracted ,parsed_email.get_region(),parsed_email.get_link(),parsed_email.get_id()]
                    subject_str = f"New Post in {group_extracted} You Might Want to Check Out!"

                    #the line below contains the list of emails that you want to recieve notifications at. You can list multiple emails if you wish (ex: email_list = ["email1@gmail.com", "email2@gmail.com"])
                    email_list = ["insert the email you want to receive notifications to here"]
                    
                    for email in email_list:
                        #TODO: INSERT EMAIL ADDRESS THAT SHOULD SEND THE EMAIL BELOW (PROBABLY WANT TO JUST PICK THE EMAIL ASSOCIATED WITH THE FACEBOOK ACCOUNT
                        emailSender2.send_message(service, "insert email here", email, subject_str , parsed_email)

                    #this step just adds the threadID to that database, this will help prevent duplicate notifications
                    threadID = message['threadId']
                    db_check.create_record(c, conn, threadID, date_extracted, uName_extracted)

            except Exception as error:
                #this code runs if something went wrong
                print('\n')
                print("An exception occurred:", error, type(error).__name__)
                print ('\n')
                pass

    print(f'found {i} messages')

if __name__ == '__main__':
    check_email()
