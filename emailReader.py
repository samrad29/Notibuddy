
import base64
from bs4 import BeautifulSoup 

group_info = [
    {'group_name': 'Buffalo Community', 'region_name':'testing', 'group_id':1},
    {'group_name': 'extra testing', 'region_name':'bologna', 'group_id':99},
    {'group_name': 'East Auroran', 'region_name':'Buffalo', 'group_id':2},
    {'group_name': 'Buffalo, NY Jobs Hiring', 'region_name':'Buffalo', 'group_id':3},
    {'group_name': 'Buffalo side jobs', 'region_name':'Buffalo', 'group_id':4},
    {'group_name': 'Buffalo Real Estate Investors Group', 'region_name':'Buffalo', 'group_id':5},
    {'group_name': 'Jamestown, NY (City of Jamestown)', 'region_name':'Buffalo', 'group_id':6},
    {'group_name': 'San Diego Real Estate Friends', 'region_name': 'SanDiego', 'group_id': 7},
    {'group_name': 'San Diego Apartments & Housing (NO SPAM) 🏡', 'region_name': 'SanDiego', 'group_id': 8},
    {'group_name': 'Realtors of San Diego California', 'region_name': 'SanDiego', 'group_id': 9},
    {'group_name': 'SAN DIEGO Real Estate Networking Group', 'region_name': 'SanDiego', 'group_id': 10},
    {'group_name': 'San Diego Real Estate Resources', 'region_name': 'SanDiego', 'group_id': 11},
    {'group_name': 'SAN DIEGO SMALL BUSINESS AND SERVICES!💅💇🔧🤝', 'region_name': 'SanDiego', 'group_id': 12},
    {'group_name': 'Mission Valley, San Diego, California Community', 'region_name': 'SanDiego', 'group_id': 13},
    {'group_name': 'San Diego Moms', 'region_name': 'SanDiego', 'group_id': 14},
    {'group_name': 'Jobs In San Diego', 'region_name': 'SanDiego', 'group_id': 15}
]

class msgClass:
    def __init__(self, uName, group, preview, date, region, link, lead_f):
        self.uName = uName
        self.group= group
        self.preview = preview
        self.date = date
        #will probably want to build functionality here to figure out what region it is?
        self.region = region
        self.link = link
        self.id = 1
        self.lead_f = lead_f


    
    def get_uName(self):
        return self.uName
    
    def get_group(self):
        return self.group
    
    def get_preview(self):
        return self.preview
    
    def get_date(self):
        return self.date

    def get_region(self):
        return self.region
    
    def get_link(self):
        return self.link
    
    def get_lead_f(self):
        return self.lead_f
    
    def get_id(self):
        return self.id


def findRegion(group):
    for grp in group_info:
        if grp['group_name'] == group:
            print(f'Region: ',grp['region_name'])
            return grp['region_name']
    print('region not found')
    return "region not found"

def read_email(msg, service):
    payload = msg['payload']
    msg_data = msg['payload']['headers']

        #finding the subject, date and sender
    for header in msg_data:
        if header['name'] ==  'Subject':
            subject  = header['value']
            #print("Subject: ", subject)
        if header['name'] == 'From':
            sender = header['value']
                       #print("Sender: ", sender)
        if header['name'] == 'Date':
            date = header['value']
                        #print("Date: ", date)  
                #getting the labels on the email              
    #lbl_out_Str = "Labsl: "
    region = "Region Not Found"
    x = 0
    
    #for lbl in msg['labelIds']: 
        #look through the lbl's tied to the email and find the ones related to facebook, when found look for the attached region
    #    lbl_obj = service.users().labels().get(userId='sakejohn79@gmail.com', id=lbl).execute()
        #lbl_out_Str = lbl_out_Str + lbl_obj['name'] + " | "
    #    labelName = lbl_obj['name']
    #    labelGroup = labelName.find('Facebook Group')
        # will need to change this to reference some label to region mapping document
    #    if labelGroup >= 0 and x == 0:
    #        start_group_name = labelGroup + 14
    #        region = findRegion(labelName[start_group_name:])
    #        x += 1
                
    #decoding the message body
    parts = payload.get('parts')[0]
    data = parts['body']['data']
    data = data.replace("-","+").replace("_","/")
    decoded_data = base64.b64decode(data)

    soup = BeautifulSoup(decoded_data , "lxml")
    body = soup.body()
                #print("Message: ", body)
    body_str = str(body)
                #print('\n')
                
                # add message data to the csv - eventually we will want to save out to a gcp table most likely
                # name of user who posted
    srch_name_indx = subject.find(" posted in ", 0)
    uName = subject[:srch_name_indx].lstrip()
    print("testing: ",uName)

                #name of group it was posted in
    srch_grp_indx = srch_name_indx + 11
    group = subject[srch_grp_indx:]

    region = findRegion(group)
    print("testing2: ", group)

                #getting the day it was posted on
    srch_date_inx = date.find(":") - 3
    date_str = date[:srch_date_inx]
    print("testing3: ", date_str)

                #getting the message preview
    srch_prev_indx = body_str.find("Hi John,") + 13

    end_srch_prec_indx = body_str.rfind("\n========================================")
    prev_string_v1 = body_str[srch_prev_indx:end_srch_prec_indx]
    sub_prev_indx = prev_string_v1.find("\"")
    preview = prev_string_v1[:sub_prev_indx]
    print("testing4: ", preview)
    start_link_search = body_str.find("View on Facebook") + 18
    restricted_string = body_str[start_link_search:]
    find_end_link = restricted_string.find(";")
    link_Str = restricted_string[:find_end_link]
    print("LINK TESTING: ", link_Str)
                #check the preview to see if it is a lead or not
    lowercase_preview = preview.casefold()
    lead_check = -1
    if lowercase_preview.find("cleaning")>=0 or lowercase_preview.find("cleaner")>=0 or lowercase_preview.find("maid") >= 0: #or lowercase_preview.find("clean") > 0: #could also look for just clean here, this will work for now
        lead_check = 1
        if lowercase_preview.find("gutter cleaning") >= 0 or lowercase_preview.find("pool cleaning") >= 0 or lowercase_preview.find("dry cleaning") >= 0:
            lead_check = -1
        if lowercase_preview.find("pool cleaner") >=0 or lowercase_preview.find("dry cleaner") >=0:
            lead_check = -1
    print(f"Lead check:{lead_check}")  
    return msgClass(uName, group, preview, date, region, link_Str, lead_check)