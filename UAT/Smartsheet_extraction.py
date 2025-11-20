import smartsheet
import pandas as pd
import re
import time
def extract_demo_accounts(sheet_id,Language,smartsheet_client,mapping_dict):
    print(Language)
    sheet = smartsheet_client.Sheets.get_sheet(sheet_id)
    column_names = [col.title for col in sheet.columns]
    data = []
    for row in sheet.rows:
        row_data = []
        for cell in row.cells:
            row_data.append(cell.value)
        data.append(row_data)

    

    df = pd.DataFrame(data, columns=column_names)
    df=df[df['Portal Health']=='Green']
    df = df.replace('Portuguese (Brazilian)', 'Portuguese')
    # print(len)
    # print(df)
    # print(list(df.columns))
    demo_accounts=[]
    for index, row in df.iterrows():
        if row['Language']=='Singaporean':
            row['Language']='English'
        
            # print(row['Language'])

        if row['Language']=='LAR Spanish':
             row['Language']='LARSpanish'
    

    df_lang=df[df['Language']==Language]

    for index, row in df_lang.iterrows():
        
        if row['Portal Health'] == 'Green':
            
            language_value_fltr = re.sub(r'\(.*?\)', '',row['Language']).strip()
            demo_user_email_value_fltr = row['Demo user email']
            password_value_fltr = row['DO NOT Change: Password']
            region_value_fltr = row['Region'] 
            # if language_value_fltr=='Singaporean':
            #     language_value_fltr='English'
            country_value_fltr = re.sub(r'\(.*?\)',  '', row['Country']).strip()
            partner_relationship_value_fltr = mapping_dict[row['Business Relationship (BR) Type']]
            account_details=[demo_user_email_value_fltr,password_value_fltr,region_value_fltr,country_value_fltr,language_value_fltr,partner_relationship_value_fltr]        
        # print(account_details)
        demo_accounts.append(account_details)
        # print(demo_accounts)
    return demo_accounts

if __name__=='__main__':
    sheet_id = '6689727127545732'
    Language = 'Turkish'
    pr_mapping={'Distributor':'Distri','Master Area Partner':'MAP','T2 Solution Provider':'T2','T1 Solution Provider':'T1','Commercial Traditional Dealer':'CTD','VPA Reseller':'VPA','Technology Partner':'TP','OEM Account':'OEM','MDF Agency':'MDF','OEM Distribution':'OEM Distri','T2 Service Provider': 'T2SP'}
    connection=False
    smartsheet_client = smartsheet.Smartsheet('jcRj5NrmLZvGu1pVx3yt7MOCWX6er54FtNjaq')
    demo_accounts_data=extract_demo_accounts(sheet_id,Language,smartsheet_client,pr_mapping)
    # while not connection:
            
            
    #         try:
    #             smartsheet_client = smartsheet.Smartsheet('jcRj5NrmLZvGu1pVx3yt7MOCWX6er54FtNjaq')
    #             demo_accounts_data=extract_demo_accounts(sheet_id,Language,smartsheet_client,pr_mapping)
    #             connection=True
    #         except Exception as e:
    #             print(e)
    #             time.sleep(2)
                # connection=False
        


    print(demo_accounts_data)
    print(len(demo_accounts_data))
