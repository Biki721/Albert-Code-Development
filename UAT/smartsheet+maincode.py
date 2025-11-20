# from concurrent.futures import thread
from asyncore import read
from concurrent.futures import thread
import sched
import schedule
import time
import datetime
import module_login_lang
import modulepagetree as mpt
import VaultSample
import threading
import pandas as pd
# import merge_upload as mu
import modulenewtab as mn
import moduleemptypage as mepg
import modulebrokenlinks as mbl
# import moduletranslation as mtr
import moduletvar as mtvar
# import moduletransnemptypage as mte
# import module_trans_gram_empt as mtge
import moduletransemptyaruba as mtea
import Smartsheet_extraction as sm
import smartsheet
import marketing_pro_page_tree as mppt
import competitor_page_tree as cpt
pr_mapping={'Distributor':'Distri','Master Area Partner':'MAP','T2 Solution Provider':'T2','T1 Solution Provider':'T1','Commercial Traditional Dealer':'CTD','VPA Reseller':'VPA','Technology Partner':'TP','OEM Account':'OEM','MDF Agency':'MDF','OEM Distribution':'OEM Distri'}

def newtab(acc):
    Firstrun=mn.PRP(acc[0][0],acc[0][1],acc[0][2],acc[0][3],acc[0][4],acc[0][5])
    #print(acc[0])
    Firstrun.setUp()
    Firstrun.test_new_tab()
    Firstrun.tearDown()
    return

def page_tree(acc):
    competitor_accounts = ['demo_competitor@pproap.com','demo_mapcompetitor_solp@yopmail.com',
                           'demo_traditional_cn_competitor@pproap.com','demo_japanese_jp_competitor@pproap.com']
    for account in competitor_accounts:
        if account == acc[0][0]:
            Firstrun=cpt.PRP(acc[0][0],acc[0][1],acc[0][2],acc[0][3],acc[0][4],acc[0][5])
        else: 
            Firstrun=mpt.PRP(acc[0][0],acc[0][1],acc[0][2],acc[0][3],acc[0][4],acc[0][5])

        Firstrun.setUp()
        Firstrun.scrapecall_writetrees()
        Firstrun.tearDown()
        return
    
def marketing_page_tree(acc):

    Firstrun=mppt.PRP(acc[0][0],acc[0][1],acc[0][2],acc[0][3],acc[0][4],acc[0][5])
    Firstrun.setUp()
    Firstrun.scrapecall_writetrees()
    Firstrun.tearDown()
    return

def tvar(acc):
    Firstrun=mtvar.PRP(acc[0][0],acc[0][1],acc[0][2],acc[0][3],acc[0][4],acc[0][5])
    #Firstrun.setUp()
    Firstrun.test_tvar_check()
    Firstrun.tearDown()
    return

def broken_link(acc):
    Firstrun=mbl.PRP(acc[0][0],acc[0][1],acc[0][2],acc[0][3],acc[0][4],acc[0][5])
    Firstrun.setUp()
    Firstrun.test_multiple_broken()
    Firstrun.tearDown()
    return

def trans_empty_aruba(acc):
    Firstrun=mtea.PRP(acc[0][0],acc[0][1],acc[0][2],acc[0][3],acc[0][4],acc[0][5])    
    Firstrun.setUp()
    Firstrun.test_load_home_page()
    Firstrun.parent()
    Firstrun.tearDown()


def module(acc):
    f = open('log.txt','a+')
    f.write(str(datetime.date.today())+'\n')
    #print("ACC",acc[0],acc)
    start = time.time()

    Firstrun = module_login_lang.PRP(acc[0][0],acc[0][1],acc[0][2],acc[0][3],acc[0][4],acc[0][5]) 
    Firstrun.setUp()
    login_bool = Firstrun.login()

    if login_bool is False:
        f.write('DEMO ACCOUNT '+str(acc)+' FAILED TO LOGIN \n')
        print('DEMO ACCOUNT',acc,'FAILED TO LOGIN')
        return
    
    f.write("Login successful: "+str(acc))
    #print('Entering pg tree----------------->line 75')
    # page_tree(acc)
    # f.write("finished page tree for"+str(acc)+" and time taken is "+ str(time.time()-start)+'\n')
    
    marketing_page_tree(acc)
    f.write("finished marketing pro page tree for"+str(acc)+" and time taken is "+ str(time.time()-start)+'\n')
  
    # ##THIS ORDER SHOULDN'T BE CHANGED#################
    # trans_empty_aruba(acc)    
    # f.write("finished translation and empty page for"+str(acc)+" and time taken is "+ str(time.time()-start)+'\n')

    # tvar(acc)    
    # # f.write("finished tvar for"+str(acc)+" and time taken is "+ str(time.time()-start)+'\n')

    # broken_link(acc)
    # # f.write("finished broken link for"+str(acc)+" and time taken is "+ str(time.time()-start)+'\n')
  
    # newtab(acc)
    # # f.write("finished newtab for"+str(acc)+" and time taken is "+ str(time.time()-start)+'\n')
 
  
    
    # print("TO TRANSLATION",acc[0][-2])
    # if acc[0][-2]!="English":
    #     translation(acc)
    #     f.write("finished translation for"+str(acc)+" and time taken is "+ str(time.time()-start)+'\n')
    # empty_page(acc)
    #print(acc)

 
    
    end = time.time()
    f.write("Total time taken for all modules for the account:"+str(acc)+" is: "+str(end-start)+'\n')
    f.close()

    return

#Creating threads to parallely run all demo accounts for a given language

def done(credentials):
    # print(credentials,'///////////////')
    to_be_merged_folderpath = "Reports"
    to_be_uploaded_filepath='D:\\UAT\\WA Reports\\Aggregated Report.xlsx'
    accounts_running = []
    #thread_count = 0
    for i in range(len(credentials)):
        accounts_running.append(threading.Thread(target=module,args=([credentials[i]],)))
        
    for i in range(len(accounts_running)):
        accounts_running[i].start()
       
        
    for i in range(len(accounts_running)):
        accounts_running[i].join()
        
    # mu.aggregate(to_be_merged_folderpath)
    # mu.upload(to_be_uploaded_filepath)
  
def fetch_cred(lang):
    #VaultSample.lang_to_run=lang
    #print(VaultSample.lang_to_run)
    #print("started")
    chunks = []
    
    credentials = sm.extract_demo_accounts('6689727127545732',lang,smartsheet.Smartsheet('jcRj5NrmLZvGu1pVx3yt7MOCWX6er54FtNjaq'),pr_mapping)

    print(credentials,'kkkkkkkkkkkkkk')
    # if lang=='English':
    #     chunks.extend(credentials[x:x+2] for x in range(0, len(credentials), 2))
    # else:
    #     chunks.extend(credentials[x:x+5] for x in range(0, len(credentials), 5))
    chunks.extend(credentials[x:x+5] for x in range(0, len(credentials), 5))

    while(chunks):
        # done(chunks[0])
        chunks.pop(0)
    # import module_trans_gram_empt
    # print(credentials,'-------------')
    # print(chunks,']]]]]]]]]]]]]]]]]]]]]]]]')
    # return chunks

def read_sched(schedule_file):
    df = pd.read_excel(schedule_file)

    # print(df)
    timings = list(df['Time'])
    #print(timings)
    timings = [timings[i].strftime('%H:%M:%S') for i in range(len(timings))]
    #print(timings)
    days = list(df['Day'])
    days = [days[i].lower() for i in range(len(days))]
    language = list(df['Language'])
    return list(zip(timings,days,language))

def check_and_run():
    week_map={0:'monday',1:'tuesday',2:'wednesday',3:'thursday',4:'friday',5:'saturday',6:'sunday'}
    sched_data = read_sched('Schedule.xlsx')
    times = [sched_data[i][0] for i in range(len(sched_data))]
    
    today = week_map[datetime.datetime.now().weekday()]
    ctime = datetime.datetime.now().time().strftime("%H:%M:%S")
    #print(times)
    #print(ctime)
    if(ctime in times):
        #print(ctime,today)
        for i in range(len(sched_data)):
            #print(sched_data[i])
            if sched_data[i][0] == ctime and sched_data[i][1]==today:
                # print("HERE")
                temp=threading.Thread(target=fetch_cred,args =(sched_data[i][2],))
                temp.start()

    # mtge.run_spell()
        
# check_and_run()

#schedule.every().day.at("16:04:00").do(thread1)

while True:
    check_and_run()
    time.sleep(1)


# fetch_cred('English')