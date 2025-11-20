#THIS MODULE IDENTIFIES ONLY SPELLING ERRORS, NOT GRAMMATICAL ERRORS

# from spellchecker import SpellChecker
import enchant
import string
from re import S
import itertools
from selenium import webdriver
from date_detector import Parser
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.common.by import By
#import VaultSample
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0
import pandas as pd
import work_phase_3 as work
from inscriptis import get_text
import fasttext
import re
from bs4 import BeautifulSoup
#model = fasttext.load_model('lid.176.bin')
import ast   


def postprocess(error):
    error = ''.join([i for i in error if not i.isdigit()])
    
    error = re.sub('\W+',' ',error)
    
    error=error.strip()
    if len(error)<=1:
        return ''
    #print(type(error))
    return error 

def grammatical_errors(extracted_text,tbi,articletitles,language): #    errors = grammatical_errors(content,find_all_example,art_titles_tocheck,lang)
    # print("EXTRACTED TEXT:,",extracted_text)
    codes= {'French':'fr','German':'de','Italian':"it",'Chinese':'zh-cn','Russian':'ru','Portugese':'pt','Indonesian':'id','Singaporean':'en','Korean':"ko",'Turkish':"tr",'Japanese':"ja",'Taiwan':"zh-tw",'Spanish':'es',"LARSpanish":'es','English':'en'}
    df = pd.read_excel('glossary.xlsx')
    tbc = 'en'
    col_name = 'en-US'
    check_list = list(df[col_name])
    ignored = "*+^#%$),(!@_}{[]?><~=\|-:;"
    extras = ['ARTIKEL','Tools catalog102030','© Copyright 2022 Hewlett Packard Enterprise Development, L.P.','Competenza','Cancella','decrescente','Presidente','ARTíCULO','Competencia Partner Ready','5000','6000']
    check_list = [check_list[i] for i in range(len(check_list)) if type(check_list[i])==str]
    tbi.extend(extras)
    tbi = [tbi[i] for i in range(len(tbi)) if tbi[i].strip()]
    gramm_checks = []

    for line in extracted_text:
        if line!='':
            gramm_checks.append(line)
        
    gramm_res = []
    gramm_checks_new=[]


    for i in range(len(gramm_checks)):
        if not gramm_checks[i][0]=="/" and not gramm_checks[i][0].isalnum():
            for m in ignored:
                gramm_checks[i]=gramm_checks[i].lstrip(m)
        flag = False
        for k in range(len(tbi)):
            if tbi[k].strip() == gramm_checks[i].strip():
                flag = True
        if flag == False:
            gramm_checks_new.append(gramm_checks[i])
    gramm_checks = gramm_checks_new
    gramm_checks.extend(articletitles)


    # print('GRAMM CHECKS LIST',gramm_checks)

    # try:
    #     for i in gramm_checks:
    #         #print (i)
    #         lst = i.split('.')
    #         for j in lst:
    #             if j and len(j)>2:
    #                 res = spell_gramm(j, check_list)
    #                 gramm_res.append(res)
    try:
        gramm_res = spell_gramm(gramm_checks, check_list)
        #print(gramm_res)
    except Exception as e:
        print('\nEXCEPTION-------------------------', e,'\n')

    # for i in range(len(gramm_checks)):
    #     gramm_checks[i]=gramm_checks[i].strip()

    #     if (gramm_checks[i]=="*"   or gramm_checks[i]=="" or gramm_checks[i].startswith("/") or gramm_checks[i].startswith("o ")):
    #         continue
    #     for k in ignored:
    #         if gramm_checks[i].startswith(k) and gramm_checks:
    #             gramm_checks[i]=gramm_checks[i].lstrip(k)
    #             gramm_checks[i]=gramm_checks[i].strip()

    #     else:
    #         for j in range(len(check_list)):
    #             if check_list[j] in gramm_checks[i]:
    #                 gramm_checks[i]=gramm_checks[i].replace(check_list[j],'')
    #     if (gramm_checks[i]):
    #         probable_errors.append(gramm_checks[i])
    # #probable_errors.extend(articletitles)
    # errors=[]
    # for i in probable_errors:
    #     gramm_res = spell_gramm(i)
    #     try:
    #         gramm_res = spell_gramm(i)
    #         if gramm_res:
    #             errors.append(gramm_res)

    #     except:
    #         print('\nERROR IN GRAMMAR CHECK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
    # print("PROBABLE ERRORS",probable_errors)
    # for i in probable_errors:
    #     try:
    #         #lang = model.predict(i)[0][0][9:]
    #         if lang=='en':
    #             i=i.strip()
    #             i = postprocess(i)
    #             if i!='':
                
                   
    #                 errors.append(i)
        
    #     except:
    #         #print("error in language prediction")
    #         continue

    #print("****************************************************************")
    # final_res = []
    # for i in gramm_res:
    #     fin_err = i.split('.')
    #     for ii in fin_err:
    #         if '{{' in ii:
    #             final_res.append(ii) 

    print("ERRORS BEFORE FINALLY RETURNING",gramm_res)
    
    return gramm_res

def callable_extract(link,html_page,soup,lang):
    content=''
    #trans_terms={'French':'Français','German':'Deutsch','Italian':"Italiano",'Chinese':'简体中文','Russian':'Русский','Portugese':'Português','Indonesian':'Bahasa indonesia','Korean':"한국어",'Turkish':"Türkçe",'Japanese':"日本語",'Taiwan':"中文（台灣)",'Spanish':'Español',"LARSpanish":'Español'}
    #trans_errors={}
    find_all_example=[]
    tbi = ["span","h1","h2","a",'div',"tr"]
    tb = ['portlet-title-text','hide','hide-accessible','hide User','sr-only','iconText','hide isPureHPE','dateFormat','size','categoryName','categoryDescription','boldContent','detailedContentText','articleSummary','articleDeails row','controlsPagination pull-right','articleDownloadHeader','articleformatSize',"border_bottom",'articleDownloadContent']
    errors = []
    art_titles_tocheck=[]
    #html_page = self.driver.page_source
    #soup=BeautifulSoup(html_page,'html.parser')
    #art_titles_tocheck=articlenamechecker(soup, 'English')
    art_titles_tocheck = articlenamechecker(soup, 'English')
    # print("doctitles",art_titles_tocheck)
    if link.strip()=='https://partner.hpe.com/group/prp' or link.strip()=="https://partner.hpe.com/group/prp/home":
        # print("inscriptis called")
        content = get_text(html_page)
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
        
        try:
            content=soup.find(id='main-content').get_text()
        except:

            pass
        content=content.splitlines()
        for i in range(len(content)):
            content[i]=" ".join(content[i].split())
        content=[content[i] for i in range(len(content)) if content[i]]

        for element in tbi:
            if element=='a':
                for word in soup.find_all(element):
                    temp=word.get_text()
                    temp=temp.splitlines()
                    find_all_example.extend(temp)
            for ele in tb:
                for word in soup.find_all(element,class_= ele):
                    temp=word.get_text()
                    temp=temp.splitlines()
                    find_all_example.extend(temp)
        for word in soup.find_all("p",id="qsUserData"):
            temp=word.get_text()
            temp=temp.splitlines()
            find_all_example.extend(temp)
        for i in range(len(find_all_example)):
            find_all_example[i]=" ".join(find_all_example[i].split())
        find_all_example=[find_all_example[i] for i in range(len(find_all_example)) if find_all_example[i]]
    # content.extend(art_titles_tocheck)
    #print("LINK:",link)
    errors = grammatical_errors(content,find_all_example,art_titles_tocheck,lang)
    
    parser=Parser()
    for i in range(len(errors)):
        for match in parser.parse(errors[i]):
            errors[i] = errors[i].replace(match.text,"")
    errors=[errors[i] for i in range(len(errors)) if errors[i]]

        
    # print("FINAL",errors)  
    return errors
    
###################### Function to check for spelling errors #######################
def spell_gramm(content, check_list):
    # print('CONTENT---------',content)
    # print(matches)
    error_list = []
    spell = enchant.DictWithPWL("en_US", "CUSTOM_SPELLING_DICT.txt")       
    for i in content:
        sentence = i.split('.')

        for i in sentence:
            words = i.split()
            corrected_text = i
            for word in words:
                if not any(char.isupper() for char in word[1:]): #Treat all words which have uppercase letters after the first letter as abbreviations or product names
                    # print('WORD:---',word)
                    if word.isalpha() and not spell.check(word) and word not in check_list:
                        suggestions = spell.suggest(word)
                        corrected_word = suggestions[0] if suggestions else word
                        corrected_text = corrected_text.replace(word, '{{' + word + "--->" + corrected_word + '}}')
                        if corrected_text not in error_list and '{{' in corrected_text:
                            error_list.append(corrected_text)


    return error_list


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
