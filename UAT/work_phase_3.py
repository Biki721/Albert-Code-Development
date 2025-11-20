# from numpy import source
import pandas as pd
import re
import ast
import docx


def round_robin(issues,f_emails):
    no_of_fixers = len(f_emails)
    #print(issues)
    allocation ={}
    j=0
    for i in range(no_of_fixers):
        allocation.update({f_emails[i]:[]})
    for issue in list(issues):
        allocation[f_emails[j]].append(issue)
        #print(allocation)
        j=(j+1)%no_of_fixers
        #print(issues)
        #print("ALLOC",allocation) 
    issues.clear()
    #print(allocation)
    return allocation
def getIndexes(dfObj, value):
    ''' Get index positions of value in dataframe i.e. dfObj.'''
    if 'Error Link' in dfObj.columns:
        rows = dfObj.index[dfObj['Error Link'] == value].tolist()
        return rows
    listOfPos = list()
    # Get bool dataframe with True at positions where the given value exists
    result = dfObj.isin([value])
    # Get list of columns that contains the value
    seriesObj = result.any()
    columnNames = list(seriesObj[seriesObj == True].index)
    # Iterate over list of columns and fetch the rows indexes where value exists
    for col in columnNames:
        rows = list(result[col][result[col] == True].index)
        for row in rows:
            listOfPos.append(row)
    # Return a list of tuples indicating the positions of value in the dataframe
    return listOfPos

def filter_content(report_df,alloc_df,tag,lang,category) : # Eg. filter_content(portalad,alloc_df,'Portal Admin',language,cat)
    issues = list(report_df['Error Link'])
    # print(alloc_df['Category'])
    alloc_df['Category'] = alloc_df['Category'].str.strip()
    # print('@@@@@@@@@',alloc_df['Category'])
    alloc_tag= alloc_df[alloc_df['Category']==tag]
    # print("Alloc tag",alloc_tag)
    alloc_tag['Module']=alloc_tag['Module'].str.strip()
    # Normalize Language values to avoid whitespace mismatch
    if 'Language' in alloc_tag.columns:
        alloc_tag['Language'] = alloc_tag['Language'].astype(str).str.strip()
    lang = str(lang).strip()
    # print(alloc_tag['Module'])
    module_avail = list(alloc_tag['Module'])  
    # print(module_avail)  
    if category in module_avail:
            alloc_tag = alloc_tag[alloc_tag['Module']==category]
    
    avail_lang = list(alloc_tag['Language'])
    if lang in avail_lang:
            alloc_tag = alloc_tag[alloc_tag['Language']==lang]
 
    # Build a clean list of fixer emails (strings only, split on newlines, stripped, non-empty)
    raw_email_col = list(alloc_tag.get("Fixers Email", []))
    emails: list[str] = []
    for ele in raw_email_col:
        if isinstance(ele, str):
            for piece in ele.split('\n'):
                piece = piece.strip()
                if piece:
                    emails.append(piece)
    # Decide allocation robustly
    if len(emails) >= 2:
        allocation = round_robin(issues, emails)
    elif len(emails) == 1:
        allocation = {emails[0]: issues}
    else:
        # No fixers configured for this filter; return empty allocation
        # print(f"No fixers found for tag={tag}, lang={lang}, category={category}")
        allocation = {}
    # print('***************',allocation) 
    return allocation

def work_alloc_execute(reportfile,allocationfile,arubapath):
    
    #base_dict= {'Invalid Links':'Content','Translation Error':'Content','Image blurriness':'Content','Broken Link':'Content','New Tab':'Content','Einstein':'Portal Admin','?t variable':'Content',"Empty Page":'Content'} 
    df_original = pd.read_excel(reportfile)
    # print('ORIGINAL',df_original)
    language= df_original["Language"][0]
    cat=df_original['Category'][0]
    df = df_original.copy()
    # print('8887777777777',df)
    with open(arubapath,"r+",encoding="utf-8") as f:
        al= f.read().splitlines()
    categorization = []
    xls = pd.ExcelFile(allocationfile)
    sheet_cache = {}
    df['Error Link'] = df['Error Link']+"*"+df['Link']
    errors = list(df['Error Link'])
    regions = df['Region'].to_list()
    #newly addded   
    demo_account = df['Demo Account'].to_list()

    # aruba = []
    # hybrid =[]
    portal_admin = []


    # err_cat = list(df['Category'])
    # print(df)
    for i in range(len(errors)):

        error_cat = ''
        if any(account in ['demo_competitor@pproap.com', 'demo_mapcompetitor_solp@yopmail.com'] for account in demo_account):
            
            if ('notifications' in str(errors[i].split('*')[0]).strip() or 'tools' in str(errors[i].split('*')[0]).strip() or 'settings' in str(errors[i].split('*')[0]).strip()):
                # print(err_cat[i])
                portal_admin.append(errors[i])
                error_cat = 'CP'
            # elif str(errors[i].split('*')[0]).strip() in al:
            #     aruba.append(errors[i])
            #     error_cat = 'A'
            else:
                # hybrid.append(errors[i])
                error_cat = 'CH'


        elif 'marketingpro' in str(errors[i].split('*')[0]).strip():
            print('Marketing Pro')
            if ('notifications' in str(errors[i].split('*')[0]).strip() or 'tools' in str(errors[i].split('*')[0]).strip() or 'settings' in str(errors[i].split('*')[0]).strip()):
            # print(err_cat[i])
                portal_admin.append(errors[i])
                error_cat = 'MP'

            # elif str(errors[i].split('*')[0]).strip() in al:
            #     aruba.append(errors[i])
            #     error_cat = 'A'
            else:
                # hybrid.append(errors[i])
                error_cat = 'MH'
            
            print(error_cat)
             

        else:
            # if (err_cat[i]!='Translation Error'):
            #      print('!!!!',err_cat[i])
            if ('notifications' in str(errors[i].split('*')[0]).strip() or 'tools' in str(errors[i].split('*')[0]).strip() or 'settings' in str(errors[i].split('*')[0]).strip()):
                # print(err_cat[i])
                portal_admin.append(errors[i])
                error_cat = 'P'

            # elif str(errors[i].split('*')[0]).strip() in al:
            #     aruba.append(errors[i])
            #     error_cat = 'A'
            else:
                # hybrid.append(errors[i])
                error_cat = 'H'

        categorization.append(error_cat)
    
    # print("Aruba",aruba)
    # print("Hybrid",hybrid)
    df['Categorization'] = categorization
    print('Categorization',df['Categorization'])
    # print('^^^^^^^^^^^^^\n',df)
    df_reference = df
   
    allocation={}
    
    
    df_APJ_PRP = df[df['Region']=="APJ"]
    df_EMEA_PRP= df[df['Region']=="EMEA"]
    df_AMS_PRP = df[df['Region']=="AMS"]
    df_NAR_PRP = df[df['Region']=="NAR" ]
    df_LAR_PRP = df[df['Region']=="LAR" ]
    df_AMS_PRP = pd.concat([df_NAR_PRP,df_LAR_PRP,df_AMS_PRP])

    df_APJ_Marketing = df[df['Region']=="APJ"]
    df_EMEA_Marketing= df[df['Region']=="EMEA"]
    df_AMS_Marketing = df[df['Region']=="AMS"]
    df_NAR_Marketing = df[df['Region']=="NAR" ]
    df_LAR_Marketing = df[df['Region']=="LAR" ]
    df_AMS_Marketing = pd.concat([df_NAR_Marketing,df_LAR_Marketing,df_AMS_Marketing])

    df_APJ_Competitor = df[df['Region']=="APJ"]
    df_EMEA_Competitor= df[df['Region']=="EMEA"]
    df_AMS_Competitor = df[df['Region']=="AMS"]
    df_NAR_Competitor = df[df['Region']=="NAR" ]
    df_LAR_Competitor = df[df['Region']=="LAR" ]
    df_AMS_Competitor = pd.concat([df_NAR_Competitor,df_LAR_Competitor,df_AMS_Competitor])
     
    if (not(df_APJ_PRP.empty)):
        if 'PRP_APJ' in sheet_cache:
            alloc_df = sheet_cache['PRP_APJ']
        else:
            alloc_df = pd.read_excel(xls,sheet_name='PRP_APJ')
            sheet_cache['PRP_APJ'] = alloc_df
        allocation1={}
        # print('**\n',alloc_df)
        #base_dict= {'Translation Error':'Content','Image blurriness':'Content','Broken Link':'Content','New Tab':'Content','?t variable':'Content',"Empty Page":'Content'}
        hybrid_apj = df_APJ_PRP[df_APJ_PRP['Categorization']=='H']
        
        portalad = df_APJ_PRP[df_APJ_PRP['Categorization']=='P']
        # print(portalad)
        allocation1.update(filter_content(portalad,alloc_df,'Portal Admin',language,cat))
        
        allocation1.update(filter_content(hybrid_apj,alloc_df,'Hybrid',language,cat))
        
        allocation = { key:allocation.get(key,[])+allocation1.get(key,[]) for key in set(list(allocation.keys())+list(allocation1.keys())) }
        #   print("111",allocation)

    if (not(df_EMEA_PRP.empty)):
        if 'PRP_EMEA' in sheet_cache:
            alloc_df = sheet_cache['PRP_EMEA']
        else:
            alloc_df = pd.read_excel(xls,sheet_name='PRP_EMEA')
            sheet_cache['PRP_EMEA'] = alloc_df
        allocation1={}
        # print('**\n',alloc_df)
        #base_dict= {'Translation Error':'Content','Image blurriness':'Content','Broken Link':'Content','New Tab':'Content','?t variable':'Content',"Empty Page":'Content'}
        hybrid_emea = df_EMEA_PRP[df_EMEA_PRP['Categorization']=='H']
        # aruba_emea = df_EMEA_PRP[df_EMEA_PRP['Categorization']=='A']
        portalad = df_EMEA_PRP[df_EMEA_PRP['Categorization']=='P']
        # print(portalad)
        allocation1.update(filter_content(portalad,alloc_df,'Portal Admin',language,cat))
        # print(allocation1)
        allocation1.update(filter_content(hybrid_emea,alloc_df,'Hybrid',language,cat))
        # print(allocation1)
        # allocation1.update(filter_content(aruba_emea,alloc_df,'Aruba',language,cat))
        # print(allocation1)
        #print(allocation1,"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        allocation = { key:allocation.get(key,[])+allocation1.get(key,[]) for key in set(list(allocation.keys())+list(allocation1.keys())) }
        print("111",allocation)

    if (not(df_AMS_PRP.empty)):

        if 'PRP_AMS' in sheet_cache:
            alloc_df = sheet_cache['PRP_AMS']
        else:
            alloc_df = pd.read_excel(xls,sheet_name='PRP_AMS')
            sheet_cache['PRP_AMS'] = alloc_df
        #print("Alloc df")
        #allocation3 = filter_content(df_AMS_PRP,alloc_df,'Hybrid',language,cat)
        #print("ALLOCATION3",allocation3)
        hybrid_ams = df_AMS_PRP[df_AMS_PRP['Categorization']=='H']
        # aruba_ams = df_AMS_PRP[df_AMS_PRP['Categorization']=='A']
        portalad = df_AMS_PRP[df_AMS_PRP['Categorization']=='P']
        allocation3 = {}
        allocation3.update(filter_content(portalad,alloc_df,'Portal Admin',language,cat))
        allocation3.update(filter_content(hybrid_ams,alloc_df,'Hybrid',language,cat))
        # allocation3.update(filter_content(aruba_ams,alloc_df,'Aruba',language,cat)) 
        allocation = { key:allocation.get(key,[])+allocation3.get(key,[]) for key in set(list(allocation.keys())+list(allocation3.keys())) }
        # print("333",allocation)
    if (not(df_APJ_Marketing.empty)):

        if 'Marketing_APJ' in sheet_cache:
            alloc_df = sheet_cache['Marketing_APJ']
        else:
            alloc_df = pd.read_excel(xls,sheet_name='Marketing_APJ')
            sheet_cache['Marketing_APJ'] = alloc_df
        #print("Alloc df")
        #allocation3 = filter_content(df_AMS_PRP,alloc_df,'Hybrid',language,cat)
        #print("ALLOCATION3",allocation3)
        hybrid_apj = df_APJ_Marketing[df_APJ_Marketing['Categorization']=='MH']
        # aruba_apj = df_APJ_Marketing[df_APJ_Marketing['Categorization']=='A']
        portalad = df_APJ_Marketing[df_APJ_Marketing['Categorization']=='MP']
        allocation4 = {}
        allocation4.update(filter_content(portalad,alloc_df,'Portal Admin',language,cat))
        allocation4.update(filter_content(hybrid_apj,alloc_df,'Hybrid',language,cat))
        # allocation4.update(filter_content(aruba_apj,alloc_df,'Aruba',language,cat)) 
        allocation = { key:allocation.get(key,[])+allocation4.get(key,[]) for key in set(list(allocation.keys())+list(allocation4.keys())) }
        # print("333",allocation)

    if (not(df_EMEA_Marketing.empty)):

        if 'Marketing_EMEA' in sheet_cache:
            alloc_df = sheet_cache['Marketing_EMEA']
        else:
            alloc_df = pd.read_excel(xls,sheet_name='Marketing_EMEA')
            sheet_cache['Marketing_EMEA'] = alloc_df
        #print("Alloc df")
        #allocation3 = filter_content(df_AMS_PRP,alloc_df,'Hybrid',language,cat)
        #print("ALLOCATION3",allocation3)
        hybrid_emea = df_EMEA_Marketing[df_EMEA_Marketing['Categorization']=='MH']
        # aruba_emea = df_EMEA_Marketing[df_EMEA_Marketing['Categorization']=='A']
        portalad = df_EMEA_Marketing[df_EMEA_Marketing['Categorization']=='MP']
        allocation5 = {}
        allocation5.update(filter_content(portalad,alloc_df,'Portal Admin',language,cat))
        allocation5.update(filter_content(hybrid_emea,alloc_df,'Hybrid',language,cat))
        # allocation5.update(filter_content(aruba_emea,alloc_df,'Aruba',language,cat)) 
        allocation = { key:allocation.get(key,[])+allocation5.get(key,[]) for key in set(list(allocation.keys())+list(allocation5.keys())) }
        print("333",allocation)
    
    if (not(df_AMS_Marketing.empty)):

        if 'Marketing_AMS' in sheet_cache:
            alloc_df = sheet_cache['Marketing_AMS']
        else:
            alloc_df = pd.read_excel(xls,sheet_name='Marketing_AMS')
            sheet_cache['Marketing_AMS'] = alloc_df
        #print("Alloc df")
        #allocation3 = filter_content(df_AMS_PRP,alloc_df,'Hybrid',language,cat)
        #print("ALLOCATION3",allocation3)
        hybrid_ams = df_AMS_Marketing[df_AMS_Marketing['Categorization']=='MH']
        # aruba_ams = df_AMS_Marketing[df_AMS_Marketing['Categorization']=='A']
        portalad = df_AMS_Marketing[df_AMS_Marketing['Categorization']=='MP']
        allocation6 = {}
        allocation6.update(filter_content(portalad,alloc_df,'Portal Admin',language,cat))
        allocation6.update(filter_content(hybrid_ams,alloc_df,'Hybrid',language,cat))
        # allocation6.update(filter_content(aruba_ams,alloc_df,'Aruba',language,cat)) 
        allocation = { key:allocation.get(key,[])+allocation6.get(key,[]) for key in set(list(allocation.keys())+list(allocation6.keys())) }
        # print("333",allocation)

    if (not(df_APJ_Competitor.empty)):

        if 'Competitor_APJ' in sheet_cache:
            alloc_df = sheet_cache['Competitor_APJ']
        else:
            alloc_df = pd.read_excel(xls,sheet_name='Competitor_APJ')
            sheet_cache['Competitor_APJ'] = alloc_df
        #print("Alloc df")
        #allocation3 = filter_content(df_AMS_PRP,alloc_df,'Hybrid',language,cat)
        #print("ALLOCATION3",allocation3)
        hybrid_apj = df_APJ_Competitor[df_APJ_Competitor['Categorization']=='CH']
        # aruba_apj = df_APJ_Competitor[df_APJ_Competitor['Categorization']=='A']
        portalad = df_APJ_Competitor[df_APJ_Competitor['Categorization']=='CP']
        allocation7 = {}
        allocation7.update(filter_content(portalad,alloc_df,'Portal Admin',language,cat))
        allocation7.update(filter_content(hybrid_apj,alloc_df,'Hybrid',language,cat))
        # allocation7.update(filter_content(aruba_apj,alloc_df,'Aruba',language,cat)) 
        allocation = { key:allocation.get(key,[])+allocation7.get(key,[]) for key in set(list(allocation.keys())+list(allocation7.keys())) }
        print("332",allocation)
    
    if (not(df_EMEA_Competitor.empty)):

        if 'Competitor_EMEA' in sheet_cache:
            alloc_df = sheet_cache['Competitor_EMEA']
        else:
            alloc_df = pd.read_excel(xls,sheet_name='Competitor_EMEA')
            sheet_cache['Competitor_EMEA'] = alloc_df
        
        hybrid_emea = df_EMEA_Competitor[df_EMEA_Competitor['Categorization']=='CH']
        # aruba_emea = df_EMEA_Competitor[df_EMEA_Competitor['Categorization']=='A']
        portalad = df_EMEA_Competitor[df_EMEA_Competitor['Categorization']=='CP']
        allocation8 = {}
        allocation8.update(filter_content(portalad,alloc_df,'Portal Admin',language,cat))
        allocation8.update(filter_content(hybrid_emea,alloc_df,'Hybrid',language,cat))
        # allocation8.update(filter_content(aruba_emea,alloc_df,'Aruba',language,cat)) 
        allocation = { key:allocation.get(key,[])+allocation8.get(key,[]) for key in set(list(allocation.keys())+list(allocation8.keys())) }
        print("333",allocation)
    

    if (not(df_AMS_Competitor.empty)):

        if 'Competitor_AMS' in sheet_cache:
            alloc_df = sheet_cache['Competitor_AMS']
        else:
            alloc_df = pd.read_excel(xls,sheet_name='Competitor_AMS')
            sheet_cache['Competitor_AMS'] = alloc_df
        #print("Alloc df")
        #allocation3 = filter_content(df_AMS_PRP,alloc_df,'Hybrid',language,cat)
        #print("ALLOCATION3",allocation3)
        hybrid_ams = df_AMS_Competitor[df_AMS_Competitor['Categorization']=='CH']
        # aruba_ams = df_AMS_Competitor[df_AMS_Competitor['Categorization']=='A']
        portalad = df_AMS_Competitor[df_AMS_Competitor['Categorization']=='CP']
        allocation9 = {}
        allocation9.update(filter_content(portalad,alloc_df,'Portal Admin',language,cat))
        allocation9.update(filter_content(hybrid_ams,alloc_df,'Hybrid',language,cat))
        # allocation9.update(filter_content(aruba_ams,alloc_df,'Aruba',language,cat)) 
        allocation = { key:allocation.get(key,[])+allocation9.get(key,[]) for key in set(list(allocation.keys())+list(allocation9.keys())) }
        print("334",allocation)
    
            

    # except:   
                
    #     allocation={}
    path = reportfile
    # print('###########################################',df)
    all_fix = list(allocation.keys())
    print(all_fix,'!!!!!!!!!!!!!!')
    for i in range(len(all_fix)):
        email=all_fix[i]
        val = allocation[all_fix[i]]
        # print(email,val)
        for j in range(len(val)):
            pos = getIndexes(df_reference,val[j])
            # print("POS",pos)
            
            df_original.loc[pos,"Mail ID"]=email
  
    # print('000000000000000000000',df)
    df_original.to_excel(path,index=None)
    
    return 


def doc_reader(filename):
    doc = docx.Document(filename)
    data = ""
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
        # print(fullText)
        data = '\n'.join(fullText)
        # print(data)
        lines=data.splitlines()
    return lines
# doc_reader('absurd_links.docx')
#
#print(os.listdir(r'D:\UAT\Reports'))

# odd_delete('Page Trees\PageTreeEMEA_Italy_Italian_Distri.txt')
# check_duplicates('Page Trees\PageTreeEMEA_Italy_Italian_Distri.txt')
# doublehttps('Page Trees\PageTreeEMEA_Italy_Italian_Distri.txt')
# revdict=reverse_dict_builder("Tree Dicts\TreeDictAPJ_Taiwan_Taiwan_T2.txt",'Page Trees\PageTreeAPJ_Taiwan_Taiwan_T2.txt')
# with open('Reverse_Internal_Dict\RIAPJ_Taiwan_Taiwan_T2.txt','w') as filehandle:
#             filehandle.write(str(revdict))
#for file in os.listdir(r'D:\UAT\Reserve'):
if __name__=='__main__':
    # work_alloc_execute('Reports\Translation_EMEA_Italy_Italian_Distri.xlsx','Fixers_list.xlsx','Aruba Urls\\ArubaAPJ_China_Chinese_T2.txt')
    work_alloc_execute('Reserve\Aggregated Report.xlsx','Fixers_list.xlsx','Aruba Urls\\ArubaAPJ_China_Chinese_T2.txt')
#delete_esm_duplicates_breadcrumbs("Page Trees\PageTreeEMEA_Spain_Spanish_Distri.txt")
