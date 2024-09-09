import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
#import base64
from datetime import datetime, timedelta
#from bs4 import BeautifulSoup 
from csv import writer
import emailSender

#import pandas as pd

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.modify']

#this is where we will map the regions to the groups
group_info = [
    {'group_name':'Testing CleanLeads SJSRDP', 'region_name':'testing', 'group_id':2},
    {'group_name': 'extra testing', 'region_name':'bologna', 'group_id':1}
]

#regions_df = pd.DataFrame(regions)


    # 1. Set up credentials and create an API client
creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    # If token.json doesn't exist, we need to authenticate the user.
if os.path.exists('token_notibuddy.json'):
        creds = Credentials.from_authorized_user_file('token_notibuddy.json')
    # If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'google_credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
    with open('token_notibuddy.json', 'w') as token:
            token.write(creds.to_json())

    # 2. Create the Gmail API service
service2 = build('gmail', 'v1', credentials=creds)

emailSender.send_message(service2, "sam@notibuddy.com", "sam.radtke99@gmail.com", "Testing" , "Please work")