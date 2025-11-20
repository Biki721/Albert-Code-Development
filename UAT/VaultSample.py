from hashlib import new
from VaultCient import fetch_secret_from_vault
import pandas as pd
import time
import datetime
import openpyxl
df = pd.read_excel('Schedule.xlsx')

'''def getlang(day,time):
    res=''
    temp=[]
    for i in range(len(df)):
        wday = df['Day'][i]
        t = df['Time'][i]
    
        if str(wday) == str(day) and str(t) <= str(time):
            # print(type(t))
            # print(type(time))
            res = df['Language'][i]
            temp.append(res)
            # return res
    print(temp)
    return temp[-1]'''


def week_number_of_month(date_value):
    return (date_value.isocalendar()[1] - date_value.replace(day=1).isocalendar()[1] + 1,date_value.isocalendar()[1])    


timestamp = time.strftime('%H:%A')
timestamp = list(timestamp.split(':'))
day = timestamp[1].strip()
time = timestamp[0]


def printweeknumber():
    mweeknumber,yweeknumber=week_number_of_month(datetime.datetime.today().date())
    return [yweeknumber]*12
    #print(yweeknumber)
    #df = pd.read_excel('Schedule.xlsx')
    #df['Week Number']=[yweeknumber]*12
    #print(df['Week Number'])

    #df.to_excel('Schedule.xlsx',index=None)
        #sheet[cellnum] = yweeknumber
    #workbook.save(filename="Schedule.xlsx")
# print(day,time)
def hashicorp(lang_to_run):
#lang_to_run = ''
#lang_to_run='English'

    if lang_to_run=="English":
        printweeknumber()


    New_Secrets = [
    'HPE_AOE_Albert_English_EMEA_Croatia_MAP', 
    # 'HPE_AOE_Albert_English_EMEA_Croatia_T2', 
    # 'HPE_AOE_Albert_English_EMEA_Lithuania _T2', 
    'HPE_AOE_Albert_English_EMEA_Lithuania _T1', 
    'HPE_AOE_Albert_English_EMEA_UK_Distri',
    'HPE_AOE_Albert_English_EMEA_UK_T2_1', 
    'HPE_AOE_Albert_English_EMEA_UK_T2_2', 
    'HPE_AOE_Albert_English_NA_USA_Distri', 
    'HPE_AOE_Albert_English_NA_Canada_CTD_1', 
    'HPE_AOE_Albert_English_NA_Canada_CTD_2', 
    # 'HPE_AOE_Albert_English_NA_USA_T2_1', 
    # 'HPE_AOE_Albert_English_NA_USA_CTD', 
    'HPE_AOE_Albert_English_NA_USA_TP', 
    'HPE_AOE_Albert_English_NA_USA_T2_2', 
    'HPE_AOE_Albert_English_NA_USA_ODP', 
    'HPE_AOE_Albert_English_NA_USA_MDF', 
    'HPE_AOE_Albert_English_NA_USA_T2_3', 
    'HPE_AOE_Albert_Chinese_APJ_China_Distri', 
    'HPE_AOE_Albert_Chinese_APJ_China_T2_1', 
    'HPE_AOE_Albert_Chinese_APJ_China_T2_2', 
    'HPE_AOE_Albert_French_EMEA_France_Distri', 
    'HPE_AOE_Albert_French_EMEA_France_T2', 
    'HPE_AOE_Albert_German_EMEA_Germany_Distri', 
    'HPE_AOE_Albert_German_EMEA_Germany_T2', 
    'HPE_AOE_Albert_Indonesian_APJ_Indonesia_T1', 
    'HPE_AOE_Albert_Indonesian_APJ_Indonesia_T2', 
    'HPE_AOE_Albert_Italian_EMEA_Italy_Distri', 
    # 'HPE_AOE_Albert_Italian_EMEA_Italy_T2', 
    'HPE_AOE_Albert_Japanese_APJ_Japan_T1_1', 
    # 'HPE_AOE_Albert_Japanese_APJ_Japan_T1_2', 
    'HPE_AOE_Albert_Japanese_APJ_Japan_T2', 
    'HPE_AOE_Albert_Korean_APJ_Korea_T2_1', 
    'HPE_AOE_Albert_Korean_APJ_Korea_T2_2', 
    'HPE_AOE_Albert_LAR_Spanish_LAR_Mexico_Distri', 
    'HPE_AOE_Albert_LAR_Spanish_LAR_Mexico_T2', 
    'HPE_AOE_Albert_Portugese_LAR_Brazil_CTD_1', 
    'HPE_AOE_Albert_Portugese_LAR_Brazil_CTD_2', 
    # # 'HPE_AOE_Albert_Russian_EMEA_Russia_Distri', 
    # # 'HPE_AOE_Albert_Russian_EMEA_Russia_T2', 
    'HPE_AOE_Albert_Singaporean_APJ_Singapore_Distri', 
    'HPE_AOE_Albert_Singaporean_APJ_Singapore_T2_1', 
    'HPE_AOE_Albert_Singaporean_APJ_Singapore_OEM', 
    'HPE_AOE_Albert_Singaporean_APJ_Singapore_T2_2', 
    'HPE_AOE_Albert_Spanish_EMEA_Spain_Distri', 
    # 'HPE_AOE_Albert_Spanish_EMEA_Spain_T2', 
    'HPE_AOE_Albert_Taiwan_APJ_Taiwan_Distri', 
    'HPE_AOE_Albert_Taiwan_APJ_Taiwan_T2_1', 
    # 'HPE_AOE_Albert_Taiwan_APJ_Taiwan_T2_2', 
    'HPE_AOE_Albert_Turkish_EMEA_Turkey_Distri', 
    # 'HPE_AOE_Albert_Turkish_EMEA_Turkey_T2'
    ]
    print(New_Secrets)


    result=[]
    try:
        for secret in New_Secrets:
            
            if lang_to_run in secret:
                credentials = fetch_secret_from_vault(secret)
                if credentials:
                    username= credentials["username"]
                    merged_password=credentials["password"]
                    password=merged_password.split("_")[0]
                    # password = 'Login2PRP!'

                    '''region = merged_password.split("_")[1]
                    country=merged_password.split("_")[2]
                    access_level=merged_password.split("_")[4]
                    language=merged_password.split("_")[3]'''

                    if 'LAR_Spanish' in secret:
                        language = 'LARSpanish'
                        region = secret.split('_')[3]
                        country = secret.split('_')[6]                    
                        access_level = secret.split('_')[7]
                    else:
                        language = secret.split('_')[3]
                        if language=='Singaporean':
                            language = 'English'
                        region = secret.split('_')[4]
                        country = secret.split('_')[5]                    
                        access_level = secret.split('_')[6]
                    
                    result.append([username,password,region,country,language,access_level])
            # print(result,'\n')

    except Exception as e:
            print("Out of schedule",e) 
            result = ''
#     result=[['demo_na_proximity@pproap.com', 'Login2PRP!', 'NAR', 'USA', 'English', 'T2'],
# ['demo_ukeng_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'UK', 'English', 'T2'],
# ['demo_unmanaged@pproap.com', 'Login2PRP!', 'NAR', 'Canada', 'English', 'CTD'], 
# ['demo_competitor@pproap.com', 'Login2PRP!', 'NAR', 'USA', 'English', 'CTD'], 
# ['demo_na_platinum@pproap.com', 'Login2PRP!', 'NAR', 'USA', 'English', 'T2'],
# ['demo_french_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'France', 'French', 'T2']]
    
    return result

# print(res)
# print(hashicorp('Indonesian'))
#print(hashicorp("Portugese"))
#printweeknumber()
# print(hashicorp('English'))
# result=[['demo_japanese_distributor@pproap.com','Login2PRP!','APJ','Japan','Japanese','Distri'],
# ['demo_japanese_jp_t2solutionprovider@pproap.com','Login2PRP!','APJ','Japan','Japanese','T1'],
# ['demo_traditional_cn_distributor@pproap.com','Login2PRP!','APJ','Taiwan','Taiwan','Distri'],
# ['demo_traditional_cn_t2solutionprovider@pproap.com','Login2PRP!','APJ','Taiwan','Taiwan','T2']]
# demo_traditional_cn_competitor@pproap.com  







# 'HPE_AOE_Albert_Portugese_LAR_Brazil_CTD_2',

# 'HPE_AOE_Albert_English_NA_USA_T2_2', 
# 'HPE_AOE_Albert_English_NA_USA_T2_3',
# 'HPE_AOE_Albert_English_EMEA_UK_T2_2', 
# 'HPE_AOE_Albert_English_NA_Canada_CTD_2',
# 'HPE_AOE_Albert_English_NA_USA_T2_2',
# 'HPE_AOE_Albert_English_NA_USA_T2_3',
# 'HPE_AOE_Albert_English_EMEA_UK_T2_2',
# 'HPE_AOE_Albert_English_NA_Canada_CTD_2', 
# 'HPE_AOE_Albert_Chinese_APJ_China_T2_2',
# 'HPE_AOE_Albert_Japanese_APJ_Japan_T1_1',
# 'HPE_AOE_Albert_Korean_APJ_Korea_T2_1',
# 'HPE_AOE_Albert_Singaporean_APJ_Singapore_T2_2',


# result=[['mapdummypartner@yopmail.com', 'Login2PRP!', 'EMEA', 'Croatia', 'English', 'MAP'],
# ['demo_mapcompetitor_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'Lithuania ', 'English', 'T2'],
# ['dummyt1map@yopmail.com', 'Login2PRP!', 'EMEA', 'Lithuania ', 'English', 'T1'], 
# ['demo_ukeng_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'UK', 'English', 'Distri'],
# ['demo_ukeng_proximity@yopmail.com', 'Login2PRP!', 'EMEA', 'UK', 'English', 'T2']]


# result=[['demo_technology@pproap.com', 'Login2PRP!', 'NAR', 'USA', 'English','TP'],
# ['demo_na_distributor@pproap.com', 'Login2PRP!', 'NAR', 'USA', 'English', 'Distri'], 
# ['test_ntwkg_gold@pproap.com', 'Login2PRP!', 'NAR', 'Canada', 'English', 'CTD'],
# ['demo_aruba@pproap.com', 'Login2PRP!', 'NAR', 'USA', 'English', 'T2'],
# ['demo_oem@pproap.com', 'Login2PRP!', 'NAR', 'USA', 'English', 'ODP'],
# ['demo_msa@pproap.com', 'Login2PRP!', 'NAR', 'USA', 'English', 'MDF']]


# result=[['demo_na_proximity@pproap.com', 'Login2PRP!', 'NAR', 'USA', 'English', 'T2'],
# ['demo_ukeng_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'UK', 'English', 'T2'],
# ['demo_unmanaged@pproap.com', 'Login2PRP!', 'NAR', 'Canada', 'English', 'CTD'], 
# ['demo_competitor@pproap.com', 'Login2PRP!', 'NAR', 'USA', 'English', 'CTD'], 
# ['demo_na_platinum@pproap.com', 'Login2PRP!', 'NAR', 'USA', 'English', 'T2']]





# , ['demo_hpelarptbr_01@pproap.com', 'Login2PRP!', 'LAR', 'Brazil', 'Portugese', 'CTD']]
#result=[['demo_turkish_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Turkey', 'Turkish', 'Distri']]
# ,['demo_turkish_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'Turkey', 'Turkish', 'T2']]
# result=[['demo_distributor_lar@pproap.com', 'Login2PRP!', 'LAR', 'Brazil', 'Portugese', 'CTD']]
# result=[['demo_h3c@pproap.com', 'Login2PRP!', 'APJ', 'China', 'Chinese', 'Distri'], ['demo_simplified_cn_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'China', 'Chinese', 'T2']]
# result=[['demo_indonesian_distributor@pproap.com', 'Login2PRP!', 'APJ', 'Indonesia', 'Indonesian', 'Distri'], ['demo_indonesian_id_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'Indonesia', 'Indonesian', 'T2']]
# result=['demo_korean_distributor@pproap.com','Login2PRP!','APJ','Korea','Korean','Distri'],['demo_korean_kr_t2solutionprovider@pproap.com','Login2PRP!','APJ','Korea','Korean','T2']

# result=[['demo_apj_distributor@pproap.com', 'Login2PRP!', 'APJ', 'Singapore', 'English', 'Distri'], ['demoapjplat@pproap.com', 'Login2PRP!', 'APJ', 'Singapore', 'English', 'T2'], ['demo_english_sg_oem@pproap.com', 'Login2PRP!', 'APJ', 'Singapore', 'English', 'OEM']]

# result=[['demo_french_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'France', 'French', 'Distri'] ,['demo_french_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'France', 'French', 'T2']]
# result=[['demo_emea_distributor@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German', 'Distri'], ['demo_emea_platinum@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German', 'T2']]
# result=[['demo_italian_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Italy', 'Italian', 'Distri'], ['demo_italian_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'Italy', 'Italian', 'T2']]
# result=[['demo_russian_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Russia', 'Russian', 'Distri'], ['demo_russian_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'Russia', 'Russian', 'T2']]
# result=[['demo_la_distributor@pproap.com', 'Login2PRP!', 'LAR', 'Mexico', 'LARSpanish', 'Distri'], ['demo_la_platinum@pproap.com', 'Login2PRP!', 'LAR', 'Mexico', 'LARSpanish', 'T2']]
# result=[['demo_spanisheu_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Spain', 'Spanish', 'Distri']]
# result=[['demo_spanisheu_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'Spain', 'Spanish', 'T2']]


