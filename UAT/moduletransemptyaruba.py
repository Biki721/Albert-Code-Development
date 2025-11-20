from concurrent.futures import thread
import work_phase_3 as work
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, StaleElementReferenceException, \
    ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.common.by import By
import ast
import datetime
from selenium import webdriver
import moduletranslation as mtrans
from bs4 import BeautifulSoup
import pandas as pd
import moduleemptypage as mep
import time
import module_login_lang
from SelectCertificate import authenticate_with_certificate
from selenium.webdriver.chrome.service import Service
import threading
import pyautogui
import pygetwindow as gw
from pynput.keyboard import Key, Controller


class PRP():
    base_url="https://partner.hpe.com"
    
    # EXCLUSION OF LINKS THAT NEED NOT UNDERGO TRANSLATION CHECKS
    links_not_to_be_checked = work.doc_reader("lte_translation.docx")
    print(links_not_to_be_checked)
    links_not_to_be_checked=[s.strip() for s in links_not_to_be_checked if s!='']

    translated_phrases={"French":"Contenu associé",'German':'Verwandter inhalt','Italian':"Contenuti correlati",'Chinese':'相关内容','Russian':'Сопутствующая информация','Portugese':'Conteúdo relacionado','Indonesian':'Konten terkait','Singaporean':'Related content','Korean':"관련 콘텐츠",'Turkish':"İlgili içerik",'Japanese':"関連コンテンツ",'Taiwan':"相關內容",'Spanish':'Contenido relacionado',"LARSpanish":'Contenido relacionado','English':'Related content'}

    # EXTRACT LIST OF LINKS THAT NEED LONGER DELAYS
    delayed_loading_links = work.doc_reader("delayed_loading.docx")
    delayed_loading_links=[s.strip() for s in delayed_loading_links if s!='']

    # EXCLUSION OF EMPTY PAGE
    not_to_check_links = work.doc_reader("lte_emptypage.docx")
    not_to_check_links=[s.strip() for s in not_to_check_links if s!='']

    # EXCLUSION OF CERTAIN SUB-DOMAINS
    absurd_links = work.doc_reader("absurd_links.docx")
    absurd_links=[s.strip() for s in absurd_links if s!='']

 
    
    def __init__(self, username: str,password: str,region:str,country,language,acc_type):
        self.username=username
        self.password=password
        if region=="NA":
            region='NAR'
        self.region=region
        self.country=country
        self.account_type=acc_type
        self.language=language
        # self.langcode=self.codes[self.language]
        # self.langtransterm=self.trans_terms[self.language]
        self.page_tree_path='Page Trees\\PageTree{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.all_links_path='All Links\\AllLinks{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.tree_dict_path='Tree Dicts\\TreeDict{r}_{c}_{l}_{a}.json'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.translation_report_path='Reports\\Translation_{r}_{c}_{l}_{a}.xlsx'.format(r=self.region,c=self.country,a=self.account_type,l=self.language)
        self.emptypage_report_path='Reports\\EmptyPage_{r}_{c}_{l}_{a}.xlsx'.format(r=self.region,c=self.country,a=self.account_type,l=self.language)
        self.phrase=self.translated_phrases[language]
        self.defaultphrase="Related content"
        self.reverse_dict_path='Reverse Dicts\\RevDict{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.aruba_links_path = 'Aruba Urls\\Aruba{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        
    def setUp(self):
        webdriver_path="Webdrivers\\chromedriver.exe"
        service = Service(webdriver_path)
        self.driver=webdriver.Chrome(service=service)
        self.driver.maximize_window()  
  

    def test_load_home_page(self):
        driver=self.driver
        wait = WebDriverWait(driver,30,poll_frequency=1,ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException])
        driver.get(self.base_url)
        wait.until(EC.element_to_be_clickable((By.ID, "oktaEmailInput"))).send_keys(self.username)
        wait.until(EC.element_to_be_clickable((By.ID, "oktaSignInBtn"))).click()
        wait.until(EC.element_to_be_clickable((By.ID, "password-sign-in"))).send_keys(self.password)
        wait.until(EC.element_to_be_clickable((By.ID, 'onepass-submit-btn'))).click()
        try:
            authenticate_with_certificate('BOT DEC-D001a')
        except Exception as e:
            print(str(e))
            try:
                authenticate_with_certificate('BOT DEC-D001a')
            except Exception as e:
                print(str(e)) 
                try:
                    print('3rd time')
                    authenticate_with_certificate('BOT DEC-D001a')
                    print('worked')
                except Exception as e:
                    print(str(e))
                    keyboard = Controller()
                    keyboard.press(Key.enter)
                    keyboard.release(Key.enter)
    
    def parent(self):
        def write_excel(errors):
            # print("writing to excel")
            fileread1=open(self.reverse_dict_path).read()
            dictionary=ast.literal_eval(fileread1)
            
            if type(errors)==dict:
                category = 'Translation Error'
                iterator = errors.keys()
                des = [errors[err] for err in errors.keys()]
                published_report_path=self.translation_report_path
            else:
                category = 'Empty Page'
                iterator = errors
                des =['Empty page']*len(errors)
                published_report_path=self.emptypage_report_path
               
            issueid = 1
    
            account=self.username
            region=self.region
            country=self.country
            language=self.language
            Fixers =''
            Fixer_mail=''
            status = "New"
            comments = "-"
            report = []
            i = 0
            for ele in iterator:
                # print("in iterator")
                if ele=="https://partner.hpe.com/group/prp/internal":
                    continue
                # ele=ele.strip()
                linkele = []
                linkele.append(issueid)
                linkele.append(account)
                linkele.append(category)
                linkele.append(region)
                linkele.append(country)
                linkele.append(language)
                if ele in dictionary:
                        length=len(dictionary[ele])
                        if length> 0:
                            s_url=dictionary[ele][-1]
                            s_url2=dictionary[ele][0]
                elif ele.strip() in dictionary:
                        length=len(dictionary[ele.strip()])
                        if length>0:
                            s_url=dictionary[ele.strip()][-1]
                            s_url2=dictionary[ele.strip()][0]
                elif ele+"\n" in dictionary:
                    length = len(dictionary[ele+"\n"])
                    if length>0:
                            s_url=dictionary[ele+"\n"][-1]
                            s_url2=dictionary[ele+"\n"][0]
                else:
                    length=0
                    
                if length==0:
                    linkele.append(ele)
                elif s_url==ele:
                    linkele.append(s_url2)
                else:
                    linkele.append(s_url)

                linkele.append(ele)
                #linkele.append(errors[ele])
                linkele.append(des[i])
                linkele.append(datetime.datetime.now())
                # linkele.append(Fixers)
                linkele.append(Fixer_mail)
                linkele.append(status)
                linkele.append(comments)
                report.append(linkele)
                issueid+=1
                i+=1
            
            # print(published_report_path)
            r = pd.DataFrame(report,columns=['Issue ID','Demo Account','Category','Region','Country','Language','Link','Error Link','Description','Time Identified','Mail ID','Status','Comments'])
            r.to_excel(published_report_path)
            return

        def integrate(site):
            self.driver.get(site)
            
            if site in self.delayed_loading_links or site.strip() in self.delayed_loading_links:
                print('SLEEPING:',site)
                time.sleep(45)
            src = self.driver.page_source
            soup=BeautifulSoup(src,'html.parser')
            # file = open('random.txt', 'a', encoding="utf-8")
            # file.write(soup)
            # file.close()
            # print(soup)
            return src,soup

        def aruba(soup):
            find_aruba = soup.find_all('span', class_='arubaTag')
            
            if find_aruba:
                return True
            return False


        def filter(list_of_links,links_not_to_be_checked):
                actual_list_of_links=[]
                list_of_links = [link.strip() for link in list_of_links]
                # print('list of link:\n',list_of_links)
                links_not_to_be_checked = [link.strip() for link in links_not_to_be_checked]
                # print('not_to_check',links_not_to_be_checked)
                actual_excluded_links = set()
                for lte in links_not_to_be_checked:
                    for ptl in list_of_links:
                        if ptl.startswith(lte) or "products" in ptl or 'https://partner.hpe.com/group/prp/settings' in ptl or ptl=='https://partner.hpe.com': #SETTINGS PAGE EXCLUSION HAD TO BE ADDED HERE  
                            actual_excluded_links.add(ptl)
                            # print('excluded:\n',actual_excluded_links)
                actual_list_of_links = list(set(list_of_links)-set(actual_excluded_links))
                # actual_list_of_links.insert(0,'https://partner.hpe.com/group/prp/home') 
                return actual_list_of_links

        f=open(self.page_tree_path,'r')
        list_of_links=f.read().splitlines()
       
        #list_of_links = ['https://partner.hpe.com','https://partner.hpe.com/group/prp/hpe-partner-ready-vantage']
        #print(list_of_links)
        #pass links not to be checked paths here
        all_links_trans = filter(list_of_links,self.links_not_to_be_checked)
        # print("to runtrans",all_links_trans)
        all_links_empty = filter(list_of_links,self.not_to_check_links)
        # print("to runempty",all_links_empty)
        #print(all_links_empty,all_links_trans)


        ##################### FUNCTION TO DETECT PAGES THAT HAVE ERROR MESSAGES ##########################
        def no_content_pg(soup):
            errmsg = ['Oops! We can’t find that page', 'We can’t find the page you’re looking for']
            text = soup.get_text()
            for msg in errmsg:
                if msg in text:
                    return True
                else:
                    return False

        errors = {}
        epterrors=[]
        aruba_links = set()
        # for link in list_of_links:
        #     #print(link)
        #     src,soup = integrate(link)
        #     #print(src,'#################')
            
        #     if aruba(soup):
        #         aruba_links.add(link)
        
        for link in list_of_links:
            # print(link,'\n*********************')
            src,soup = integrate(link)
            # print(soup)
            aruba_bool = aruba(soup)
            #print("HEY",aruba_bool)
            #print("LINK",link)
            if aruba_bool:
                if (link!='https://partner.hpe.com' and link!='https://partner.hpe.com/group/prp' and link!='https://partner.hpe.com/group/prp/home'):                    
                        #print("HOMEPAGE")
                        aruba_links.add(link)
            # print(aruba_links)
            nocontent = no_content_pg(soup)
            
            if nocontent:
                 epterrors.append(link)
                #  print(epterrors)
            if link in all_links_trans and link in all_links_empty:
                # print(self.language)
                if self.language!='English' and self.language!='Singaporean':
                    #print("inside first if")
                    err = mtrans.callable_extract(link,src,soup,self.language)
                    # print('LINK:',link,'\n',soup)
                    if err:
                        errors.update({link:err})
                epterrors.append(mep.emptypagecheck(link,self.phrase,self.defaultphrase,soup))
                # err = mtrans.callable_extract(link,src,soup,self.language)    
                # if err:
                #      errors.update({link:err})
                # epterrors.append(mep.emptypagecheck(link,self.phrase,self.defaultphrase,soup))

            elif link in all_links_empty:
                #src,soup = integrate(link)
                epterrors.append(mep.emptypagecheck(link,self.phrase,self.defaultphrase,soup))

            elif link in all_links_trans:
                #src,soup = integrate(link)
                if self.language!='English' and self.language!='Singaporean':
                    #print("second if")
                    print('LINK:',link,'\n',soup)
                    err = mtrans.callable_extract(link,src,soup,self.language)
                    if err:
                        errors.update({link:err})
                # err = mtrans.callable_extract(link,src,soup,self.language)    
                # if err:
                #      errors.update({link:err})
                epterrors.append(mep.emptypagecheck(link,self.phrase,self.defaultphrase,soup))

            else:
                continue
            # print('*****************************************************************')

        epterrors = [err for err in epterrors if err!='']
        # print(epterrors)
        write_excel(epterrors)
        # print(errors,type(errors))
        write_excel(errors)
            

        with open(self.aruba_links_path, 'w') as filehandle:
                for listitem in aruba_links:
                        filehandle.write('%s\n' % listitem)

       
        
    def tearDown(self):
        self.driver.close()
        df=pd.read_excel(self.translation_report_path)
        dff=pd.read_excel(self.emptypage_report_path)
        if len(df)>0:
            work.work_alloc_execute(self.translation_report_path,'Fixers_list.xlsx',self.aruba_links_path)
        if len(dff)>0:
            work.work_alloc_execute(self.emptypage_report_path,'Fixers_list.xlsx',self.aruba_links_path)

# credentials=[#['demo_na_proximity@pproap.com', 'Login2PRP!', 'NA', 'USA', 'English', 'CTDB'],
# #['demo_italian_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Italy', 'Italian', 'Distri'],
# # ['demo_turkish_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'Turkey', 'Turkish', 'T2'],
# # ['demo_ukeng_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'UK', 'English', 'T2A'],['demo_french_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'France', 'French', 'T2'],['demo_la_distributor@pproap.com', 'Login2PRP!', 'LAR', 'Mexico', 'LARSpanish', 'Distri'],
# #['demo_emea_platinum@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German', 'T2'],
# # ['demo_distributor_lar@pproap.com', 'Login2PRP!', 'LAR', 'Brazil', 'Portugese', 'CTD'],['demo_spanisheu_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Spain', 'Spanish', 'Distri'],
# #['demo_japanese_jp_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'Japan', 'Japanese', 'T2'],
# #['demo_simplified_cn_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'China', 'Chinese', 'T2'],
# ['demo_indonesian_distributor@pproap.com', 'Login2PRP!', 'APJ', 'Indonesia', 'Indonesian', 'Distri']]

# credentials=[#['demo_na_proximity@pproap.com', 'Login2PRP!', 'NA', 'USA', 'English', 'CTDB'],
# ['demo_italian_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Italy', 'Italian', 'Distri'],
# # # ['demo_simplified_cn_aruba@yopmail.com', 'Login2PRP!', 'APJ', 'China', 'Chinese', 'T2'],
# ['demo_hpelarptbr_01@pproap.com', 'Login2PRP!', 'LAR', 'Brazil', 'Portugese', 'CTD'],
# ['demo_french_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'France', 'French', 'T2'],['demo_la_distributor@pproap.com', 'Login2PRP!', 'LAR', 'Mexico', 'LARSpanish', 'Distri'],
# ['demo_emea_platinum@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German', 'T2'],
# ['demo_emea_distributor@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German', 'Distri'],
# ##['demo_distributor_lar@pproap.com', 'Login2PRP!', 'LAR', 'Brazil', 'Portugese', 'CTD'],
# ['demo_spanisheu_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Spain', 'Spanish', 'Distri'],
# ['demo_la_platinum@pproap.com', 'Login2PRP!', 'LAR', 'Mexico', 'LARSpanish', 'T2'],
# ['demo_japanese_jp_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'Japan', 'Japanese', 'T2'],
# ['demo_simplified_cn_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'China', 'Chinese', 'T2'],
# ['demo_turkish_distri@mailinator.com', 'Login2PRP!', 'EMEA', 'Turkey', 'Turkish', 'Distri'],
# ['demo_japanese_distributor@pproap.com','Login2PRP!','APJ','Japan','Japanese','Distri'],
# ['demo_korean_kr_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'Korea', 'Korean', 'T2'],
# ['demo_traditional_cn_t2solutionprovider@pproap.com','Login2PRP!','APJ','Taiwan','Taiwan','T2']]


if __name__=='__main__':
    # credentials = [#['mapdummypartner@yopmail.com', 'Login2PRP!', 'EMEA', 'Croatia', 'English', 'MAP'], ['demo_hreng_mapt2@yopmail.com', 'Login2PRP!', 'EMEA', 'Croatia', 'English', 'T2'], 
                # ['dummyt1map@yopmail.com', 'Login2PRP!', 'EMEA', 'Lithuania', 'English', 'T1'],  
                # ['demo_ukeng_proximity@yopmail.com', 'Login2PRP!', 'EMEA', 'UK', 'English', 'T2'], ['demo_ukeng_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'UK', 'English', 'T2A']]
                # ['demo_na_distributor@pproap.com', 'Login2PRP!', 'NA', 'USA', 'English', 'Distri'], ['test_ntwkg_gold@pproap.com', 'Login2PRP!', 'NA', 'Canada', 'English', 'CTD'], 
                #     ['demo_unmanaged@pproap.com', 'Login2PRP!', 'NA', 'USA', 'English', 'CTD'], ['demo_competitor@pproap.com', 'Login2PRP!', 'NA', 'USA', 'English', 'CTDA'], 
                #     ['demo_na_proximity@pproap.com', 'Login2PRP!', 'NA', 'USA', 'English', 'CTDB'], ['demo_na_platinum@pproap.com', 'Login2PRP!', 'NA', 'USA', 'English', 'T2']]
                #     ['demo_aruba@pproap.com', 'Login2PRP!', 'NA', 'USA', 'English', 'T2A'], ['demo_msa@pproap.com', 'Login2PRP!', 'NA', 'USA', 'English', 'MDF'], 
                #     ['demo_aruba@pproap.com', 'Login2PRP!', 'NA', 'USA', 'English', 'T2A'], ['demo_apj_distributor@pproap.com', 'Login2PRP!', 'APJ', 'Singapore', 'English', 'Distri'], 
                #     ['demoapjplat@pproap.com', 'Login2PRP!', 'APJ', 'Singapore', 'English', 'T2'],
                # ['demo_ukeng_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'UK', 'English', 'Distri'],
                # ['demo_aruba@pproap.com', 'Login2PRP!', 'NA', 'USA', 'English', 'T2A']]
                # ['demo_japanese_jp_competitor@pproap.com', 'Login2PRP!','APJ','Japan','Japanese','T2']]
                # ['demo_korean_distributor@pproap.com','Login2PRP!','APJ','Korea','Korean','Distri'],
                # ['demo_apj_distributor@pproap.com', 'Login2PRP!', 'APJ', 'Singapore', 'English', 'Distri']]
                # ['demo_emea_distributor@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German', 'Distri']]
                # ['demo_japanese_distributor@pproap.com','Login2PRP!','APJ','Japan','Japanese','Distri']]
                # ['demo_indonesian_distributor@pproap.com', 'Login2PRP!', 'APJ', 'Indonesia', 'Indonesian', 'Distri']]
                # ['demo_simplified_cn_aruba@yopmail.com', 'Login2PRP!', 'APJ', 'China', 'Chinese', 'T2'],
                # ['demo_korean_distributor@pproap.com','Login2PRP!','APJ','Korea','Korean','Distri']]
                # ['demo_english_sg_oem@pproap.com', 'Login2PRP!', 'APJ', 'Singapore', 'English', 'OEM'],
                #     ['demo_english_sg_proximity@pproap.com', 'Login2PRP!', 'APJ', 'Singapore', 'English', 'CTD']]
    
    # credentials = [['demo_spanisheu_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Spain', 'Spanish', 'Distri'],
    #                ['demo_french_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'France', 'French', 'Distri'],
    #                ['demo_emea_platinum@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German', 'T2'],
    #                ['demo_korean_distributor@pproap.com','Login2PRP!','APJ','Korea','Korean','Distri'],
    #                ['demo_italian_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Italy', 'Italian', 'Distri'],
    #                ['demo_la_platinum@pproap.com', 'Login2PRP!', 'LAR', 'Mexico', 'LARSpanish', 'T2'],
    #                ['demo_turkish_distri@mailinator.com', 'Login2PRP!', 'EMEA', 'Turkey', 'Turkish', 'Distri'],
    #                ['demo_emea_distributor@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German', 'Distri'],
    #                ['demo_simplified_cn_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'China', 'Chinese', 'T2'],
    #                ['demo_la_distributor@pproap.com', 'Login2PRP!', 'LAR', 'Mexico', 'LARSpanish', 'Distri'],
    #                ['demo_korean_kr_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'Korea', 'Korean', 'T2'],
    #                ['demo_japanese_jp_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'Japan', 'Japanese', 'T2'],
    #                ['demo_french_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'France', 'French', 'T2'],
    #                ['demo_traditional_cn_distributor@pproap.com','Login2PRP!','APJ','Taiwan','Taiwan','Distri'],
    #                ['demo_traditional_cn_t2solutionprovider@pproap.com','Login2PRP!','APJ','Taiwan','Taiwan','T2'],
    #                ['demo_simplified_cn_aruba@yopmail.com', 'Login2PRP!', 'APJ', 'China', 'Chinese', 'T2'],
    #                ['demo_h3c@pproap.com', 'Login2PRP!', 'APJ', 'China', 'Chinese', 'Distri'],
    #                ['demo_distributor_lar@pproap.com', 'Login2PRP!', 'LAR', 'Brazil', 'Portugese', 'CTD'],
    #                ['demo_traditional_cn_competitor@pproap.com','Login2PRP!','APJ','Taiwan','Taiwan','CTD'],
    #                ['demo_hpelarptbr_01@pproap.com', 'Login2PRP!', 'LAR', 'Brazil', 'Portugese', 'CTD'],
    #                ['demo_indonesian_distributor@pproap.com', 'Login2PRP!', 'APJ', 'Indonesia', 'Indonesian', 'Distri'],
    #                ['demo_japanese_distributor@pproap.com','Login2PRP!','APJ','Japan','Japanese','Distri'],
    #                ['demo_indonesian_id_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'Indonesia', 'Indonesian', 'T2'],
    #                ['demo_japanese_jp_competitor@pproap.com','Login2PRP!','APJ','Japan','Japanese','T1']]
    credentials=[
        # ['demo_korean_distributor@pproap.com','Login2PRP!','APJ','Korea','Korean','Distri'],
        # ['demo_italian_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Italy', 'Italian', 'Distri'],
        # ['demo_japanese_distributor@pproap.com','Login2PRP!','APJ','Japan','Japanese','Distri'],
        # ['demo_french_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'France', 'French', 'Distri'],
        ['demo_french_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'France', 'French', 'T2']]
        # ['demo_indonesian_id_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'Indonesia', 'Indonesian', 'T2'],
        # ['demo_turkish_distri@mailinator.com', 'Login2PRP!', 'EMEA', 'Turkey', 'Turkish', 'Distri'],
        # ['demo_emea_platinum@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German', 'T2'],
        # ['demo_spanisheu_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Spain', 'Spanish', 'Distri'],
        # ['demo_simplified_cn_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'China', 'Chinese', 'T2'],
        # ['demo_emea_distributor@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German', 'Distri'],
        # ['demo_korean_kr_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'Korea', 'Korean', 'T2']]
    for acc in credentials:
        # Firstrun = module_login_lang.PRP(acc[0],acc[1],acc[2],acc[3],acc[4],acc[5]) 
        # Firstrun.setUp()
        # login_bool = Firstrun.login()
        # if login_bool is False:
        #     print('DEMO ACCOUNT',acc,'FAILED TO LOGIN')

        while True:
            print(acc[0])
            try:
                Firstrun=PRP(acc[0],acc[1],acc[2],acc[3],acc[4],acc[5])
                #Firstrun.text_extract()
                Firstrun.setUp()
                Firstrun.test_load_home_page()

                Firstrun.parent()
                Firstrun.tearDown()
                print("going into the next account")
                break  # If login is successful, break out of the while loop
            except Exception as e:
                print("Login failed:", str(e))
                print("Retrying the same file...")
        
        # Firstrun=PRP(acc[0],acc[1],acc[2],acc[3],acc[4],acc[5])
        # #Firstrun.text_extract()
        # Firstrun.setUp()
        # Firstrun.test_load_home_page()

        # Firstrun.parent()
        # Firstrun.tearDown()
        # print("going into the next account")