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

def filter_content(report_df,alloc_df,base_dict,lang,category) :
   

    issues = list(report_df['Error Link'])
    # error_links=list()
    # error_linksreport_df['Link'])
    # print(issues)
    # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    #print("yoo",report_df.columns,report_df['Category'])
    
    
    fix_emails =[]
    #print(issues)
    if category not in base_dict.keys():
        # fixers = list(alloc_df["Fixers Name"])
        emails = list(alloc_df["Fixers Email"])
        for i in range(len(emails)):
            
            fix_e = emails[i].split('\n')
            #print(fix_e,"FIXERS EMAILS")
            fix_emails.extend(fix_e)
        allocation = round_robin(issues,fix_emails)

    else:

        category_mapped = base_dict[category]
        #print("CAT MAPPED",category_mapped)
        
        alloc_filt_category = alloc_df[alloc_df['Category']==category_mapped]
        alloc_filt_category['Module']=alloc_filt_category['Module'].str.strip()
        #print("CAT",category)
        module_avail = list(alloc_filt_category['Module'])
        #module_avail = [module_avail[i].strip() for i in range(len(module_avail))]
        #print(category,module_avail)
        
        if category in module_avail:
            alloc_filt_category = alloc_filt_category[alloc_filt_category['Module']==category]
        #print(alloc_filt_category,"MODULE FILTER")
        avail_lang = list(alloc_filt_category['Language'])
        #print(avail_lang)
        if lang in avail_lang:
            
            alloc_filt_category = alloc_filt_category[alloc_filt_category['Language']==lang]
        #print("AFTER LANG FILTER",alloc_filt_category)
        # fixers = list(alloc_filt_category['Fixers Name'])
  
        emails = list(alloc_filt_category['Fixers Email'])
        #print("EMAILS",fixers,emails)
        for i in range(len(emails)):
            
            fix_e = emails[i].split('\n')
            #print(fix_e,"FIXERS EMAILS")
            #final_fixers.extend(fix)
            fix_emails.extend(fix_e)
            #print(fix_emails)
        #print(final_fixers,fix_emails)
        if (len(fix_emails)>1):
            allocation = round_robin(issues,fix_emails)
        else:
            #print(fixers,emails,issues)
            allocation = {emails[0]:issues}
        #print("allocation",allocation)
        return allocation

def work_alloc_execute(reportfile,allocationfile):
    
    base_dict= {'Invalid Links':'Content','Translation Error':'Content','Image blurriness':'Content','Broken Link':'Content','New Tab':'Content','Einstein':'Portal Admin','?t variable':'Content',"Empty Page":'Content'} 
    df_original = pd.read_excel(reportfile)
    language= df_original["Language"][0]
    cat=df_original['Category'][0]
    df = df_original.copy()
    
    df['Error Link'] = df['Error Link']+"*"+df['Link']
    df_reference = df
    err = list(df['Error Link'])
    cols = list(df.columns)
    df_pa = pd.DataFrame(columns=cols)
    if (cat!='Translation Error'):
        for i in range(len(err)):
            if ('notifications' in err[i] or 'tools' in err[i] or 'settings' in err[i]):
                df_pa.loc[len(df_pa)] = list(df.loc[i])
                df = df.drop(labels=i, axis=0)
    
    
    #print("DFPA",df_pa)
    #print("CAT",cat)
    allocation={}
    
    
    df_APJ = df[df['Region']=="APJ"]
    df_EMEA= df[df['Region']=="EMEA"]
    df_AMS = df[df['Region']=="AMS"]
    df_NAR = df[df['Region']=="NAR" ]
    df_LAR = df[df['Region']=="LAR" ]
    frames = [df_NAR,df_LAR,df_AMS]
    region = df_original['Region'][0]
    df_AMS=pd.concat(frames)
    if (df_original['Region'][0]=="LAR" or df_original['Region'][0]=="NAR"):
        region = 'AMS'
    # try:
    #df_pa is basically a seperation for classifying portal admin links. The links are categorized based on specific keywords after the report is generated. The issues in dfpa are directly sent for work allocation.
    if not(df_pa.empty):

        temp = base_dict.copy()
        temp[cat]='Portal Admin'
        alloc_df = pd.read_excel(allocationfile,sheet_name=region)
        allocation0 = filter_content(df_pa,alloc_df,temp,language,cat)
        # print
        #print("ALLOCATION0",allocation0)
        allocation.update(allocation0)

    if (not(df_APJ.empty)):
        alloc_df = pd.read_excel(allocationfile,sheet_name='APJ')
        #base_dict= {'Translation Error':'Content','Image blurriness':'Content','Broken Link':'Content','New Tab':'Content','?t variable':'Content',"Empty Page":'Content'}

        allocation1 = filter_content(df_APJ,alloc_df,base_dict,language,cat)
        #print(allocation1,"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        allocation = { key:allocation.get(key,[])+allocation1.get(key,[]) for key in set(list(allocation.keys())+list(allocation1.keys())) }
        #   print("111",allocation)
        
    if (not(df_EMEA.empty)):
        alloc_df = pd.read_excel(allocationfile,sheet_name='EMEA')
        allocation2 = filter_content(df_EMEA,alloc_df,base_dict,language,cat)
        #print("ALLOC2",allocation2)
        #   print('allocation2:',allocation2)
        allocation = { key:allocation.get(key,[])+allocation2.get(key,[]) for key in set(list(allocation.keys())+list(allocation2.keys())) }
        
        #   print("222",allocation)
    if (not(df_AMS.empty)):

        alloc_df = pd.read_excel(allocationfile,sheet_name='AMS')
        #print("Alloc df")
        allocation3 = filter_content(df_AMS,alloc_df,base_dict,language,cat)
        #print("ALLOCATION3",allocation3)
        allocation = { key:allocation.get(key,[])+allocation3.get(key,[]) for key in set(list(allocation.keys())+list(allocation3.keys())) }
        # print("333",allocation)
    
    #print("ALL ALLOCATION",allocation)
    # except:
    #     allocation={}
    path = reportfile
    #print(df)
    all_fix = list(allocation.keys())
    for i in range(len(all_fix)):
        email=all_fix[i]
        val = allocation[all_fix[i]]
        for j in range(len(val)):
            pos = getIndexes(df_reference,val[j])
            #print("POS",pos)
            
            df_original.loc[pos,"Mail ID"]=email
  
    # print(df)
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

#
#print(os.listdir(r'D:\UAT\Reports'))

# odd_delete('Page Trees\PageTreeEMEA_Italy_Italian_Distri.txt')
# check_duplicates('Page Trees\PageTreeEMEA_Italy_Italian_Distri.txt')
# doublehttps('Page Trees\PageTreeEMEA_Italy_Italian_Distri.txt')
# revdict=reverse_dict_builder("Tree Dicts\TreeDictAPJ_Taiwan_Taiwan_T2.txt",'Page Trees\PageTreeAPJ_Taiwan_Taiwan_T2.txt')
# with open('Reverse_Internal_Dict\RIAPJ_Taiwan_Taiwan_T2.txt','w') as filehandle:
#             filehandle.write(str(revdict))
#for file in os.listdir(r'D:\UAT\Reserve'):
work_alloc_execute(r'Reports\\Translation_EMEA_Germany_German_T2.xlsx','Fixers_list.xlsx')
#delete_esm_duplicates_breadcrumbs("Page Trees\PageTreeEMEA_Spain_Spanish_Distri.txt")
