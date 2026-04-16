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
    while (issues):
        allocation[f_emails[j]].append(issues[0])
        #print(allocation)
        j=(j+1)%no_of_fixers
        #print(issues)
        issues.pop(0)
        #print("ALLOC",allocation) 
    #print(allocation)
    return allocation
def getIndexes(dfObj, value):
    ''' Get index positions of value in dataframe i.e. dfObj.'''
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
            for piece in re.split(r'[\n,;]+', ele):
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
    # print('***************') 
    return allocation

def work_alloc_execute(reportfile,allocationfile,arubapath):
    
    #base_dict= {'Invalid Links':'Content','Translation Error':'Content','Image blurriness':'Content','Broken Link':'Content','New Tab':'Content','Einstein':'Portal Admin','?t variable':'Content',"Empty Page":'Content'} 
    df_original = pd.read_excel(reportfile)
    # print('ORIGINAL',df_original)
    language= df_original["Language"][0]
    cat=df_original['Category'][0]
    df = df_original.copy()
    # print('8887777777777',df)
    f=open(arubapath,"r+")
    al= f.read().splitlines()
    categorization = []
    df['Error Link'] = df['Error Link']+"*"+df['Link']
    errors = list(df['Error Link'])
    aruba = []
    hybrid =[]
    portal_admin = []
    err_cat = list(df['Category'])
    # print(df)
    for i in range(len(errors)):

        # if (err_cat[i]!='Translation Error'):
        #      print('!!!!',err_cat[i])
        error_cat = ''
        if ('notifications' in str(errors[i].split('*')[0]).strip() or 'tools' in str(errors[i].split('*')[0]).strip() or 'settings' in str(errors[i].split('*')[0]).strip()):
            # print(err_cat[i])
            portal_admin.append(errors[i])
            error_cat = 'P'

        elif str(errors[i].split('*')[0]).strip() in al:
            aruba.append(errors[i])
            error_cat = 'A'
        else:
            hybrid.append(errors[i])
            error_cat = 'H'

        categorization.append(error_cat)
    
    # print("Aruba",aruba)
    # print("Hybrid",hybrid)
    df['Categorization'] = categorization
    # print('^^^^^^^^^^^^^\n',df)
    df_reference = df
    err = list(df['Error Link'])
    cols = list(df.columns)
    # df_pa = pd.DataFrame(columns=cols)
    
        # for i in range(len(err)):
        #     if ('notifications' in err[i] or 'tools' in err[i] or 'settings' in err[i]):
        #         df_pa.loc[len(df_pa)] = list(df.loc[i])
        #         df = df.drop(labels=i, axis=0)
    
    
    #print("DFPA",df_pa)
    #print("CAT",cat)
    allocation={}
    
    
    df_APJ = df[df['Region']=="APJ"]
    df_EMEA= df[df['Region']=="EMEA"]
    df_AMS = df[df['Region']=="AMS"]
    df_NAR = df[df['Region']=="NAR" ]
    df_LAR = df[df['Region']=="LAR" ]
    frames = [ df_NAR,df_LAR,df_AMS]
    region = df_original['Region'][0]
    df_AMS=pd.concat(frames)
    if (df_original['Region'][0]=="LAR" or df_original['Region'][0]=="NAR"):
        region = 'AMS'
    # try:
    #df_pa is basically a seperation for classifying portal admin links. The links are categorized based on specific keywords after the report is generated. The issues in dfpa are directly sent for work allocation.
    # if not(df_pa.empty):

    #     # print("PA!!!",df_pa)
    #     alloc_df = pd.read_excel(allocationfile,sheet_name=region)
    #     allocation0 = filter_content(df_pa,alloc_df,'Portal Admin',language,cat)
    #     # print("ALLOCATION0",allocation0)
    #     allocation.update(allocation0)

    if (not(df_APJ.empty)):
        alloc_df = pd.read_excel(allocationfile,sheet_name='APJ')
        allocation1={}
        # print('**\n',alloc_df)

        #base_dict= {'Translation Error':'Content','Image blurriness':'Content','Broken Link':'Content','New Tab':'Content','?t variable':'Content',"Empty Page":'Content'}
        hybrid_apj = df_APJ[df_APJ['Categorization']=='H']
        aruba_apj = df_APJ[df_APJ['Categorization']=='A']
        portalad = df_APJ[df_APJ['Categorization']=='P']
        # print(portalad)
        allocation1.update(filter_content(portalad,alloc_df,'Portal Admin',language,cat))
        # print(allocation1)
        allocation1.update(filter_content(hybrid_apj,alloc_df,'Hybrid',language,cat))
        # print(allocation1)
        allocation1.update(filter_content(aruba_apj,alloc_df,'Aruba',language,cat))
        # print(allocation1)
        #print(allocation1,"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        allocation = { key:allocation.get(key,[])+allocation1.get(key,[]) for key in set(list(allocation.keys())+list(allocation1.keys())) }
        #   print("111",allocation)
        
    if (not(df_EMEA.empty)):
        alloc_df = pd.read_excel(allocationfile,sheet_name='EMEA')
        #allocation2 = filter_content(df_EMEA,alloc_df,'Hybrid',language,cat)
        #print("ALLOC2",allocation2)
        #   print('allocation2:',allocation2)
        hybrid_emea = df_EMEA[df_EMEA['Categorization']=='H']
        aruba_emea = df_EMEA[df_EMEA['Categorization']=='A']
        portalad = df_EMEA[df_EMEA['Categorization']=='P']
        allocation2 = {}
        allocation2.update(filter_content(portalad,alloc_df,'Portal Admin',language,cat))
        allocation2.update(filter_content(hybrid_emea,alloc_df,'Hybrid',language,cat))
        allocation2.update(filter_content(aruba_emea,alloc_df,'Aruba',language,cat))        
        allocation = { key:allocation.get(key,[])+allocation2.get(key,[]) for key in set(list(allocation.keys())+list(allocation2.keys())) }
        
        #   print("222",allocation)
    if (not(df_AMS.empty)):

        alloc_df = pd.read_excel(allocationfile,sheet_name='AMS')
        #print("Alloc df")
        #allocation3 = filter_content(df_AMS,alloc_df,'Hybrid',language,cat)
        #print("ALLOCATION3",allocation3)
        hybrid_ams = df_AMS[df_AMS['Categorization']=='H']
        aruba_ams = df_AMS[df_AMS['Categorization']=='A']
        portalad = df_AMS[df_AMS['Categorization']=='P']
        allocation3 = {}
        allocation3.update(filter_content(portalad,alloc_df,'Portal Admin',language,cat))
        allocation3.update(filter_content(hybrid_ams,alloc_df,'Hybrid',language,cat))
        allocation3.update(filter_content(aruba_ams,alloc_df,'Aruba',language,cat)) 
        allocation = { key:allocation.get(key,[])+allocation3.get(key,[]) for key in set(list(allocation.keys())+list(allocation3.keys())) }
        # print("333",allocation)
    
    #print("ALL ALLOCATION",allocation)
    # except:
    #     allocation={}
    path = reportfile
    # print('###########################################',df)
    all_fix = list(allocation.keys())
    # print(all_fix,'!!!!!!!!!!!!!!')
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
    work_alloc_execute('WA Reports\\Aggregated Report.xlsx','Fixers_list.xlsx','Aruba Urls\\ArubaAPJ_China_Chinese_T2.txt')
#delete_esm_duplicates_breadcrumbs("Page Trees\PageTreeEMEA_Spain_Spanish_Distri.txt")
