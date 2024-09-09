import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
#import base64
from datetime import datetime, timedelta
#from bs4 import BeautifulSoup 
from csv import writer
import emailSender2
import emailReader
import db_check
import smsSender
import time
import sqlite3

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

#import pandas as pd

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.modify']

#this is where we will map the regions to the groups


region_info = {
     'testing': ['sam.radtke99@gmail.com', 'danielponto0@gmail.com'],
     'Buffalo': ['sam.radtke99@gmail.com', 'danielponto0@gmail.com', 'jergej1@gmai.com', 'podlasjr@gmail.com'],
     'SanDiego': ['sam.radtke99@gmail.com'],
     'region not found': ['sam.radtke99@gmail.com']
}

#regions_df = pd.DataFrame(regions)


    # 1. Set up credentials and create an API client
creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    # If token.json doesn't exist, we need to authenticate the user.
if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    # If there are no (valid) credentials available, let the user log in.
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

    # 2. Create the Gmail API service
service = build('gmail', 'v1', credentials=creds)

#getting the access token for the sam@notibuddy.com email
creds2 = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    # If token.json doesn't exist, we need to authenticate the user.
if os.path.exists('token_notibuddy.json'):
        creds2 = Credentials.from_authorized_user_file('token_notibuddy.json')
    # If there are no (valid) credentials available, let the user log in.
if not creds2 or not creds2.valid:
    if creds2 and creds2.expired and creds.refresh_token:
        creds2.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'google_credentials.json', SCOPES)
        creds2 = flow.run_local_server(port=0)
        # Save the credentials for the next run
    with open('token_notibuddy.json', 'w') as token:
            token.write(creds2.to_json())

    # 2. Create the Gmail API service
service2 = build('gmail', 'v1', credentials=creds2)



#would be good to define the mapping dataset here I am guessing - for customers

#connecting to dataset that stores sent emails




def check_email():
#adding in a step here to get the emails from just today
    now = datetime.now()
#    today_start = datetime(now.year, now.month, now.day, 0,0,0)
#    today_end = datetime(now.year, now.month, now.day, 23, 59,59)

#    today_start_str = today_start.strftime('%Y/%m/%d')
#    today_end_str = today_end.strftime('%Y/%m/%d %H:%M:%S')

#    query = f"after:{today_start_str} before: {today_end_str}"

    #emailSender2.send_message(service2, "notibuddy@notibuddy.com", "sam.radtke99@gmail.com", "testing", "mic check")
    # Call the Gmail API to fetch emails
    results = service.users().messages().list(userId='sakejohn79@gmail.com', q='is:unread AND from:Facebook').execute()
    messages = results.get('messages')
    i = 0
    if not messages:
        print('No messages found.')
    else:
        #print('Messages:')
        for message in messages:
            msg = service.users().messages().get(userId='sakejohn79@gmail.com', id=message['id']).execute()
            #service.users().messages().trash(userId='sakejohn79@gmail.com', id=message['id']).execute()
            #this check below will skip all processing below if the thread has already been found
            #if db_check.check_duplicate(c, msg) == 1: 
            #     continue;
            parsed_email = emailReader.read_email(msg, service)
            i = i + 1
            try:
                """check the database of sent emails at this point"""
                if parsed_email.get_lead_f() >= 0:
                    #send to the csv for now
                    uName_extracted = parsed_email.get_uName()
                    group_extracted = parsed_email.get_group()
                    preview_extracted = parsed_email.get_preview()
                    link = parsed_email.get_link()
                    date_extracted = parsed_email.get_date()
                    extract = [uName_extracted,group_extracted,date_extracted, preview_extracted ,parsed_email.get_region(),parsed_email.get_link(),parsed_email.get_id()]
                    subject_str = f"New Post in {group_extracted} You Might Want to Check Out!"
                    #this the finding emails code
                    # do the api call here
                    #email_list = ["sam.radtke99@gmail.com", "danielponto0@gmail.com", "jergej1@gmail.com", "podlasjr@gmail.com"]
                    region = parsed_email.get_region()
                    email_list = region_info[region]
                    for emails in email_list:
                        emailSender2.send_message(service2, "notibuddy@notibuddy.com", emails, subject_str , parsed_email)
                    
                    threadID = message['threadId']
                    db_check.create_record(c, conn, threadID, date_extracted, uName_extracted)

                    #smsSender.send(send_str) 

            except Exception as error:
                print('\n')
                print("An exception occurred:", error, type(error).__name__)
                print ('\n')
                pass

    print(f'found {i} messages')

if __name__ == '__main__':
    check_email()
    


 
# List that we want to add as a new row
#List = [6, 'William', 5532, 1, 'UAE']
 
# Open our existing CSV file in append mode
# Create a file object for this file
#with open('event.csv', 'a') as f_object:
 
    # Pass this file object to csv.writer()
    # and get a writer object
#    writer_object = writer(f_object)
 
    # Pass the list as an argument into
    # the writerow()
 #   writer_object.writerow(List)
 
    # Close the file object
  #  f_object.close()