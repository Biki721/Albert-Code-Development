import requests
import win32com.client as win32
import time
import urllib3
from datetime import datetime
import os



timeout = urllib3.util.Timeout(connect=2.0, read=1.0)
http=urllib3.PoolManager(timeout=timeout)

base_url="https://partner.hpe.com"
recipients='biki.dey@hpe.com;pranav-m.bhat@hpe.com;rohitashwyo.dutta-chowdhury@hpe.com;mrunal.vinod@hpe.com;somaiah.kodimaniyanda-lava@hpe.com;srividya-d@hpe.com;weiwei.shao@hpe.com;kalaivanan.a@hpe.com;probles@hpe.com;taoy@hpe.com'

             
def email():
        # Check and close Outlook if it's open
        try:
            # Kill outlook
            os.system('taskkill /im outlook.exe /f')
        except Exception as e:
            print(str(e))
            
        flag = False
        while not flag:
            try:
                outlook = win32.Dispatch('Outlook.application')
                mail = outlook.CreateItem(0)
                flag = True
            except Exception as e:
                print(str(e))
        print('start')
        mail.To = recipients
        # mail.To = 'biki.dey@hpe.com'
        # prpalerts@hpe.com'
        mail.Subject = 'Partner Ready Portal is down for Partners'
        mail.Body = '''Hi there! 
The Partner Ready Portal is inaccessible to partners. 
Please take necessary action as earliest.
Thank you, 
Albert salutes you.'''
        mail.Send()
        print('end') 
        return 
    
def check_portal_health(link):
    # self.email()
    try:
        r=http.request("GET",link)
    except Exception as e:
        ee=str(e)
        if "NewConnectionError" in ee or "MaxRetryError" in ee :
            time.sleep(15)
            try:
                r=http.request("GET",link)
            except Exception as e:
                ee=str(e)
                if "NewConnectionError" in ee or "MaxRetryError" in ee :
                    email()
                    print('portal down')
                    time.sleep(1800)
                
                   
                
                

        #         self.broken_links.append(link)
        # errors = [
        #     "NOT FOUND The requested resource could not be found",
        #     "Service Unavailable The server is temporarily unable to service your request. Please try again later",
        #     "Service Unavailable The server is temporarily unable to service your request due to maintenance downtime capacity",
        #     "This site can’t be reached cf-passport.it.hpe.com's server IP address could not be found",
        #     "400 Bad Request",
        #     "HTTP status 403 Request forbidden. Transaction ID: XXXXXXXXXXXXXXXXXXXXXX failed",
        #     "Service Unavailable DNS failure The server is temporarily unable to service your request. Please try again later"
        # ]
        # self.driver.get(link)
        # pgsrc = self.driver.page_source
        # # print(pgsrc,'*********')
        # for errmsg in errors:
        #     if errmsg in pgsrc:
        #         return errmsg            
 
while True:
    check_portal_health(base_url)

