
import work_phase_3 as work

import ast
import datetime
import moduletranslation as mtrans
from bs4 import BeautifulSoup
import pandas as pd
import moduleemptypage as mep
import time
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from url_utils import load_home_prefixes, is_home_redirect_selenium

HOME_PREFIXES = load_home_prefixes('config/home_pages.txt')


class PRP():
    base_url="https://partner.hpe.com"
    
    # EXCLUSION OF LINKS THAT NEED NOT UNDERGO TRANSLATION CHECKS
    links_not_to_be_checked = work.doc_reader("lte_translation.docx")
    links_not_to_be_checked=[s.strip() for s in links_not_to_be_checked if s!='']

    #Exclusion of marketing pro site links
    marketingpro_links_not_to_be_checked = work.doc_reader("Marketingpro_lte_translation.docx")
    marketingpro_links_not_to_be_checked=[s.strip() for s in marketingpro_links_not_to_be_checked if s!='']

    #Exclusion of marketing pro site links
    competitor_links_not_to_be_checked = work.doc_reader("Competitor_lte_translation.docx")
    competitor_links_not_to_be_checked=[s.strip() for s in competitor_links_not_to_be_checked if s!='']

    links_not_to_be_checked += marketingpro_links_not_to_be_checked + competitor_links_not_to_be_checked

    translated_phrases = {
        "French": "Contenu associé",
        'German': 'Verwandter inhalt',
        'Italian': "Contenuti correlati",
        'Chinese': '相关内容',
        'Chinese-Simplified': '相关内容',
        'Russian': 'Сопутствующая информация',
        'Portugese': 'Conteúdo relacionado',
        'Portuguese-Brazil': 'Conteúdo relacionado',
        'Indonesian': 'Konten terkait',
        'Singaporean': 'Related content',
        'Korean': "관련 콘텐츠",
        'Turkish': "İlgili içerik",
        'Japanese': "関連コンテンツ",
        'Taiwan': "相關內容",
        'Spanish': 'Contenido relacionado',
        "LARSpanish": 'Contenido relacionado',
        'English': 'Related content'
    }

    # EXTRACT LIST OF LINKS THAT NEED LONGER DELAYS
    delayed_loading_links = work.doc_reader("delayed_loading.docx")
    delayed_loading_links=[s.strip() for s in delayed_loading_links if s!='']

    # EXCLUSION OF EMPTY PAGE
    not_to_check_links = work.doc_reader("lte_emptypage.docx")
    not_to_check_links=[s.strip() for s in not_to_check_links if s!='']

    marketingpro_not_to_check_links = work.doc_reader("marketingpro_lte_emptypage.docx")
    marketingpro_not_to_check_links=[s.strip() for s in marketingpro_not_to_check_links if s!='']

    not_to_check_links += marketingpro_not_to_check_links

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
        self.page_tree_path='Page Trees\\PageTree{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.all_links_path='All Links\\AllLinks{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.tree_dict_path='Tree Dicts\\TreeDict{r}_{c}_{l}_{a}.json'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.translation_report_path='Reports\\Translation_{r}_{c}_{l}_{a}.xlsx'.format(r=self.region,c=self.country,a=self.account_type,l=self.language)
        self.emptypage_report_path='Reports\\EmptyPage_{r}_{c}_{l}_{a}.xlsx'.format(r=self.region,c=self.country,a=self.account_type,l=self.language)
        self.phrase=self.translated_phrases[language]
        self.defaultphrase="Related content"
        self.reverse_dict_path='Reverse Dicts\\RevDict{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.aruba_links_path = 'Aruba Urls\\Aruba{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        self.competitor_accounts = ['demo_competitor@pproap.com','demo_mapcompetitor_solp@yopmail.com']

    def setUp(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        self.page.set_default_timeout(30000)
  

    def test_load_home_page(self):
        page = self.page

        page.goto(self.base_url)

        page.fill("#oktaEmailInput", self.username)
        page.click("#oktaSignInBtn")
        page.fill("#password-sign-in", self.password)
        page.click("#onepass-submit-btn")

        try:
            page.wait_for_selector('//*[@id="form19"]/div[2]/div[2]/div[2]/a', timeout=40000)
            page.click('//*[@id="form19"]/div[2]/div[2]/div[2]/a')
        except PlaywrightTimeoutError:
            print("Login redirect click failed")
        except Exception:
            pass

        time.sleep(5)
        page.goto(self.base_url)
        
   
    def parent(self):
        def write_excel(errors):
            # print("writing to excel")
            fileread1=open(self.reverse_dict_path).read()
            dictionary=ast.literal_eval(fileread1)

            if self.username not in self.competitor_accounts:
                fileread2=open(self.marketingpro_reverse_dict_path).read()
                dictionary1=ast.literal_eval(fileread2)
            else:
                dictionary1 = {}

            dictionary = {**dictionary,**dictionary1}

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
            page = self.page
            try:
                resp = page.goto(site, wait_until="networkidle")
            except PlaywrightTimeoutError:
                resp = None
            except Exception:
                return None, None

            if site in self.delayed_loading_links or site.strip() in self.delayed_loading_links:
                # print('SLEEPING:',site)
                time.sleep(45)

            final_url = (page.url or "").split('#')[0].rstrip('/')
            for p in HOME_PREFIXES:
                if final_url == p or final_url.startswith(p):
                    return None, None

            try:
                src = page.content()
            except Exception:
                return None, None
            soup = BeautifulSoup(src, 'html.parser')
            return src, soup

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
                # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',actual_list_of_links)
                # actual_list_of_links.insert(0,'https://partner.hpe.com/group/prp/home') 
                return actual_list_of_links

        # f=open(self.page_tree_path,'r')
        # list_of_links=f.read().splitlines()

        f=open(self.page_tree_path,'r')
        list_of_links = f.read().splitlines()
        # print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^',list_of_links)
        
        all_links_trans = filter(list_of_links,self.links_not_to_be_checked)
        # print("to runtrans",all_links_trans)
        all_links_empty = filter(list_of_links,self.not_to_check_links)
        # print("to runempty",all_links_empty)


        ##################### FUNCTION TO DETECT PAGES THAT HAVE ERROR MESSAGES ##########################
        def no_content_pg(soup):
            errmsg = ["Oops! We can't find that page", "We cant find the page you're looking for"]
            text = soup.get_text()
            for msg in errmsg:
                if msg in text:
                    return True
            return False

        errors = {}
        epterrors=[]
        aruba_links = set()
        
        for link in list_of_links:
            # print(link,'\n*********************')
            src,soup = integrate(link)
            if src is None:
                # Redirected to homepage, skip this link
                continue

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

            elif link in all_links_empty:
                #src,soup = integrate(link)
                epterrors.append(mep.emptypagecheck(link,self.phrase,self.defaultphrase,soup))

            elif link in all_links_trans:
                #src,soup = integrate(link)
                if self.language!='English' and self.language!='Singaporean':
                    #print("second if")
                    # print('LINK:',link,'\n',soup)
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
        try:
            if self.context is not None:
                self.context.close()
        except Exception:
            pass
        try:
            if self.browser is not None:
                self.browser.close()
        except Exception:
            pass
        try:
            if self.playwright is not None:
                self.playwright.stop()
        except Exception:
            pass

        df = pd.read_excel(self.translation_report_path)
        dff = pd.read_excel(self.emptypage_report_path)
        if len(df) > 0:
            work.work_alloc_execute(self.translation_report_path, 'Fixers_list.xlsx', self.aruba_links_path)
        if len(dff) > 0:
            work.work_alloc_execute(self.emptypage_report_path, 'Fixers_list.xlsx', self.aruba_links_path)

def run_account(account):
    try:
        # First login module
        # prp_login = module_login_lang.PRP(*account)
        # prp_login.setUp()
        # login_bool = prp_login.login()
        
        # if not login_bool:
        #     print('DEMO ACCOUNT', account, 'FAILED TO LOGIN')
        #     prp_login.tearDown()
        #     return
        
        # time.sleep(20)
        # prp_login.tearDown()

        # New session for actual scraping
        prp_main = PRP(*account)
        prp_main.setUp()
        prp_main.test_load_home_page()
        prp_main.parent()
        prp_main.tearDown()
        
        from playsound3 import playsound
        playsound("C:/Users/deyb/Downloads/beep-01a.wav")
        print(f"Finished processing: {account[0]}")
    except Exception as e:
        print(f"Exception while processing {account[0]}: {e}")


if __name__=='__main__':

    credentials = [
       ["mhmg_albert_dist1@yopmail.com", "Login2Bot!", "EMEA", "Turkey", "Turkish", "T2"],
    ]

    # Adjust max_workers based on your system capability (e.g., RAM, CPU, browser limits)
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(run_account, credentials)
    