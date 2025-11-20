import os
import win32com.client as win32
from datetime import datetime

def email(message = "Dear Team, Albert run has been completed"):
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

    # mail = outlook.CreateItem(0)
    # mail.To = 'biki.dey@hpe.com;somaiah.kodimaniyanda-lava@hpe.com;srividya-d@hpe.com;ragul.subramani@hpe.com;kalaivanan.a@hpe.com;peng.wang3@hpe.com;jiaojiao.ding@hpe.com;jingz@hpe.com;weiwei.shao@hpe.com;mrunal.vinod@hpe.com'
    mail.To = 'biki.dey@hpe.com'
    # ;somaiah.kodimaniyanda-lava@hpe.com'
    # mail.To = 'pranav-m.bhat@hpe.com'
    mail.Subject ="Albert run from interface" + str(datetime.now().strftime("%b %d"))
    mail.Body = message
    # mail.Attachments.Add(excel_file_path)
    mail.Send() 
    return