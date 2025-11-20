from re import S
import itertools
from selenium import webdriver
from date_detector import Parser
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.common.by import By
import SelectCertificate
import VaultSample
import datetime
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0
import pandas as pd
import work
from inscriptis import get_text
import fasttext
import time
import re
from bs4 import BeautifulSoup
model = fasttext.load_model('lid.176.bin')
import ast


def postprocess(error):
    #ignored = "*+^#%$),(!@_}{[]?><~=\|-:;"

    error = ''.join([i for i in error if not i.isdigit()])
    
    error = re.sub('\W+',' ',error)
    
    error=error.strip()
    if len(error)<=1:
        return ''
    #print(type(error))
    return error 

def translation_errors(extracted_text,tbi,articletitles,language):
    #print("EXTRACTED TEXT:,",extracted_text)
    codes= {'French':'fr','German':'de','Italian':"it",'Chinese':'zh-cn','Russian':'ru','Portugese':'pt','Indonesian':'id','Singaporean':'en','Korean':"ko",'Turkish':"tr",'Japanese':"ja",'Taiwan':"zh-tw",'Spanish':'es',"LARSpanish":'es','English':'en'}
    df = pd.read_excel('glossary.xlsx')
    tbc = codes[language]
    col_name = tbc+"-"+tbc.upper()
    check_list = list(df[col_name])
    ignored = "*+^#%$),(!@_}{[]?><~=\|-:;"
    extras = ['ARTIKEL','Tools catalog102030','© Copyright 2023 Hewlett Packard Enterprise Development, L.P.','Competenza','Cancella','decrescente','Presidente','ARTíCULO','Competencia Partner Ready','5000','6000','fors','As a Service','h','© Copyright 2022 Hewlett Packard Enterprise Development, L.P.']
    check_list = [check_list[i] for i in range(len(check_list)) if type(check_list[i])==str]
    # print("check list",check_list)
    tbi.extend(extras)
    tbi = [tbi[i] for i in range(len(tbi)) if tbi[i].strip()]
    #print(tbi)
    translation_checks = []
    for line in extracted_text:
        if line!='':
            translation_checks.append(line)
    #print(translation_checks)    
    probable_errors=[]
    translation_checks_new=[]
    for i in range(len(translation_checks)):
        if not translation_checks[i][0]=="/" and not translation_checks[i][0].isalnum():
            for m in ignored:
                translation_checks[i]=translation_checks[i].lstrip(m)
        flag = False
        for k in range(len(tbi)):
            if tbi[k].strip() == translation_checks[i].strip():
                flag = True
        if flag== False:
            translation_checks_new.append(translation_checks[i])
    translation_checks= translation_checks_new
    # file = open('random.txt', 'w', encoding='utf-8')
    # file.write(translation_checks)
    # file.close()
    #print(translation_checks)
    translation_checks.extend(articletitles)

    for i in range(len(translation_checks)):
        translation_checks[i]=translation_checks[i].strip()

        if (translation_checks[i]=="*"   or translation_checks[i]=="" or translation_checks[i].startswith("/") or translation_checks[i].startswith("o ")):
            continue
        for k in ignored:
            if translation_checks[i].startswith(k) and translation_checks:
                translation_checks[i]=translation_checks[i].lstrip(k)
                translation_checks[i]=translation_checks[i].strip()

        else:
            for j in range(len(check_list)):
                # if check_list[j]=="Copyright Development L P":
                #     print("MAIN PROBABLE CULPRIT",translation_checks[i],check_list[j])
                if check_list[j] in translation_checks[i]:
                    translation_checks[i]=translation_checks[i].replace(check_list[j],'')
        if (translation_checks[i]):
            probable_errors.append(translation_checks[i])
    
    #probable_errors.extend(articletitles)
    errors=[]
    # print("PROBABLE ERRORS",probable_errors)

###############################################################################################################
    for i in probable_errors:
        
        try:
            # lang = model.predict(i)[0][0][9:]
            labels, predictions = model.predict(i, k=-1, threshold=0.02)
            languages = {label.split("__")[-1]: probability for label, probability in zip(labels, predictions)}

            # print('\nCONTENT:',i)
            # print('PREDICTED LANGUAGE:',languages)
            if tbc=='zh-cn' or tbc=='zh-tw':
                tbc = 'zh'
            # print('PREFERRED LANG:',tbc,'\n')

            if tbc=='pt':
                if 'pt' not in languages and 'es' not in languages:
                    i = i.strip()
                    i = postprocess(i)
                    if len(i)>1 and i not in check_list:                   
                        errors.append(i)

            else:
                if tbc not in languages:
                    i = i.strip()
                    i = postprocess(i)
                    if len(i)>1 and i not in check_list:                   
                        errors.append(i)
                        # print(i)
        
        except Exception as e:
            # print("\nERROR IN LANG PRED:",e,'\n')
            continue

######################## COMMENT THE ABOVE FOR LOOP AND UNCOMMENT THE FOR LOOP BELOW TO CHECK FOR ONLY ENGLISH ##########################

    # for i in probable_errors:
    #     try:
    #         lang = model.predict(i)[0][0][9:]
    #         if lang=='en':
    #             i=i.strip()
    #             i = postprocess(i)
    #             if i!='':
                
                   
    #                 errors.append(i)
        
    #     except:
    #         #print("error in language prediction")
    #         continue
###########################################################################################################


    # print("****************************************************************")
    # print("ERRORS BEFORE FINALLY RETURNING",errors)
    return list(set(errors))

def articlenamechecker(soupobject,language_translation):
    article_info={}
    possible_errors=[]
    try:
        results=soupobject.find_all('span',class_='articleDownloadHeader')
        res=soupobject.find_all('span',class_='articleformatSize')
    except:
        #print("Donno")
        return possible_errors
    else:
        for (articlename,articledesc) in itertools.zip_longest(results,res):
            if articledesc.get_text().strip() is not None and len(articledesc.get_text().strip())>0 :
                article_info[articledesc.get_text().strip()]=articlename.get_text().strip()
    for ele in article_info:
        if language_translation in ele:
            possible_errors.append(article_info[ele])
    # print(article_info)
    return possible_errors


def callable_extract(link,html_page,soup,lang):
    # print('randommmmmmmm')
    content=''
    trans_terms={'French':'Français','German':'Deutsch','Italian':"Italiano",'Chinese':'简体中文','Russian':'Русский','Portugese':'Português','Indonesian':'Bahasa indonesia','Korean':"한국어",'Turkish':"Türkçe",'Japanese':"日本語",'Taiwan':"中文（台灣)",'Spanish':'Español',"LARSpanish":'Español'}
    #trans_errors={}
    find_all_example=[]
    tbi=["span","h1","h2","a",'div',"tr"]
    #tbi = []
    tb= ['portlet-title-text','hide','hide-accessible','hide User','sr-only','iconText','hide isPureHPE','dateFormat','size','categoryName','categoryDescription','boldContent','detailedContentText','articleSummary','articleDeails row','controlsPagination pull-right','articleDownloadHeader','articleformatSize',"border_bottom",'articleDownloadContent']
    #tb = []
    errors = []
    art_titles_tocheck=[]
    #html_page = self.driver.page_source
    #soup=BeautifulSoup(html_page,'html.parser')
    art_titles_tocheck=articlenamechecker(soup,trans_terms[lang])
    # print("doctitles",art_titles_tocheck)
    if link.strip()=='https://partner.hpe.com/group/prp' or link.strip()=="https://partner.hpe.com/group/prp/home":
        # print("inscriptis called")
        content = get_text(html_page)
        # print(content)
        content=content.splitlines()
        for element in tbi:
            if element=='a':
                for word in soup.find_all(element):
                    find_all_example.append(word.get_text().strip())
            for ele in tb:
                for word in soup.find_all(element,class_= ele):
                        find_all_example.append(word.get_text())
        for i in range(len(content)):
            content[i]=content[i].strip()
            if content[i].startswith("+"):
                content[i]=content[i].lstrip("+")
                content[i]=content[i].strip()

    else:
        # content=soup.find(id='main-content').get_text()
        try:
            content=soup.find(id='main-content').get_text()
        #     # file = open('random.txt', 'w', encoding='utf-8')
        #     # file.write(content)
        #     # file.close()
        except:

            pass
        content=content.splitlines()
        # print('\n********',content)

        for i in range(len(content)):
            content[i]=" ".join(content[i].split())
        content=[content[i] for i in range(len(content)) if content[i]]
        # print('^^^^^^', content)

        for element in tbi:
            if element=='a':
                for word in soup.find_all(element):
                    temp=word.get_text()
                    temp=temp.splitlines()
                    find_all_example.extend(temp)
            for ele in tb:
                for word in soup.find_all(element,class_= ele):
                    
                    temp=word.get_text()
                    #print(element, ele, temp,'***************')
                    temp=temp.splitlines()
                    find_all_example.extend(temp)
                    
        for word in soup.find_all("p",id="qsUserData"):
            temp=word.get_text()
            temp=temp.splitlines()
            find_all_example.extend(temp)
        for i in range(len(find_all_example)):
            find_all_example[i]=" ".join(find_all_example[i].split())
        find_all_example=[find_all_example[i] for i in range(len(find_all_example)) if find_all_example[i]]
        # print(find_all_example)
    # content.extend(art_titles_tocheck)
    #print("LINK:",link)
    errors= translation_errors(content,find_all_example,art_titles_tocheck,lang)
    
    parser=Parser()
    for i in range(len(errors)):
        for match in parser.parse(errors[i]):
            errors[i] = errors[i].replace(match.text,"")
    errors=[errors[i] for i in range(len(errors)) if errors[i]]

        
    # print("FINAL",errors)  
    return errors
    
  
         
       