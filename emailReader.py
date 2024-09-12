
import base64
from bs4 import BeautifulSoup 

#just defining the msgClass
class msgClass:
    def __init__(self, uName, group, preview, date, region, link, lead_f):
        self.uName = uName
        self.group= group
        self.preview = preview
        self.date = date
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


#ignore this
def findRegion(group):
    return "region not found"

#this is the most important thing here. this function takes in a gmail message object and a gmail API service connection. Then it returns a msgClass object.
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

    #this region thing has to do with some functionality that we ended up scrapping
    region = "Region Not Found"
    x = 0
    
    #This is where we decode and parse through the actual message body
    parts = payload.get('parts')[0]
    data = parts['body']['data']
    data = data.replace("-","+").replace("_","/")
    decoded_data = base64.b64decode(data)

    soup = BeautifulSoup(decoded_data , "lxml")
    body = soup.body()
                
    body_str = str(body) #putting the message body in string format


    #Now we have the message body as well as the subject in string format and can use some string functions to find the info we need
    
    #this block looks through the subject of the email to get the user who posted
    srch_name_indx = subject.find(" posted in ", 0)
    uName = subject[:srch_name_indx].lstrip()
    print("testing: ",uName)

    #here we look through the subject to find the group that the post was in
    srch_grp_indx = srch_name_indx + 11
    group = subject[srch_grp_indx:]

    #Ignore this
    region = findRegion(group)
    print("testing2: ", group)

    #getting the date it was posted on
    srch_date_inx = date.find(":") - 3
    date_str = date[:srch_date_inx]
    print("testing3: ", date_str)

    #This block finds the text that the Facebook user actually posted. 
    srch_prev_indx = body_str.find("Hi ") + 18
    end_srch_prec_indx = body_str.rfind("\n========================================")
    prev_string_v1 = body_str[srch_prev_indx:end_srch_prec_indx]
    sub_prev_indx = prev_string_v1.find("\"")
    preview = prev_string_v1[:sub_prev_indx]
    print("testing4: ", preview)

    #this part extracts a link to the post
    start_link_search = body_str.find("View on Facebook") + 18
    restricted_string = body_str[start_link_search:]
    find_end_link = restricted_string.find(";")
    link_Str = restricted_string[:find_end_link]
    print("LINK TESTING: ", link_Str)

    # Okay this is where it checks the post (within the email) for any keywords (the key words we have setup are "cleaning", "cleaner", and "maid". 
    # We are also excluding emails that contain "pool cleaning" "dry cleaning" "pool cleaner" or "dry cleaner"
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
