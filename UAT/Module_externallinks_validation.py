import pandas as pd
import datetime
import ast
import openpyxl
from playwright.sync_api import sync_playwright
import work
import External_validation_functions as ext
from concurrent.futures import ThreadPoolExecutor
from metric_report import log_module_metric
from pathlib import Path

BASE_DIR = Path(__file__).parent

class PRP():
    xpathlist = []
    Errormsg = []
    excel_file_path = 'Error messages for external URL\Error messages for external URL.xlsx'
    sheetname = 'Error_message'
    delayed_loading_links=work.doc_reader(str(BASE_DIR /"delayed_loading.docx"))
    delayed_loading_links=[s.strip() for s in delayed_loading_links if s!=''] 
    absurd_links =work.doc_reader(str(BASE_DIR /"absurd_links.docx"))
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
        self.page_tree_path=BASE_DIR/'Page Trees/PageTree{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,a=self.account_type,l=self.language)
        self.report_path=BASE_DIR/'Reports/External_links{r}_{c}_{l}_{a}.xlsx'.format(r=self.region,c=self.country,a=self.account_type,l=self.language)
        self.tree_dict_path=BASE_DIR/'Tree Dicts/TreeDict{r}_{c}_{l}_{a}.json'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.aruba_links_path = BASE_DIR/'Aruba Urls/Aruba{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.external_links_path = BASE_DIR/'External Urls/External{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.reverse_dict_path=BASE_DIR/'Reverse Dicts/RevDict{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.pw = None
        self.browser = None
        self.page = None

    def setUp(self):
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        # ✅ Increase default timeout
        self.page.set_default_timeout(60000)  # 60 seconds instead of 120
        self.page.set_default_navigation_timeout(45000)  # 45 seconds for navigation
        self.driver = self.page
        self.wait = None
    

    def read_external_excel(self):
        xpathlist = []
        sheetname = 'Error_message'
        excel_file_path = BASE_DIR /'Error messages for external URL'/'Error messages for external URL.xlsx'
        df_errmsg = pd.read_excel(excel_file_path, sheet_name=sheetname)
        Errormsg = df_errmsg['message'].tolist() 
        Errormsg = [s.strip() for s in Errormsg if s != '']
        # print(Errormsg)

        
        wb = openpyxl.load_workbook(excel_file_path)
        worksheet = wb['URL_credential']
        # print(worksheet,'&&&&&&&&&&&&&&&&&&&&&&&&')
        
        for row in worksheet.iter_rows():   
            row_values = []
            for cell in row:
                row_values.append(cell.value)
            xpathlist.append(row_values)
        wb.close() 
        # print(xpathlist)
        return Errormsg,xpathlist
    
    
    # print("list of xpath*****************",xpathlist)
    @log_module_metric("External Links")
    def external_url_validation(self):
        import time
        
        driver = self.driver
        wait = self.wait
        errorlinks = []
        seismic_l1 = []
        psnow_l1 = []
        hpelearning_l1 = []
        certification_l1 = []
        vshow_l1 = []
        
        Errormsg, xpathlist = self.read_external_excel()
        
        seis_login_link = xpathlist[1][0]
        hpe_learlogin_link = xpathlist[3][0]
        psnow_login_link = xpathlist[5][0]
        vshow_login_link = xpathlist[2][0]
        
        with open(self.external_links_path, 'r') as f:
            Ext_path = f.read().splitlines()
        
        # Categorize links
        for link in Ext_path:
            if 'seismic' in link:
                seismic_l1.append(link)
            elif 'psnow' in link:
                psnow_l1.append(link)
            elif 'mylearning' in link:
                hpelearning_l1.append(link)
            elif 'certification' in link:
                certification_l1.append(link)
            elif 'vshow.' in link:
                vshow_l1.append(link)
        
        # ✅ ADD PROGRESS TRACKING
        total_links = len(seismic_l1) + len(psnow_l1) + len(hpelearning_l1) + len(certification_l1) + len(vshow_l1)
        
        print("\n" + "="*70)
        print("🚀 EXTERNAL LINK VALIDATION STARTED")
        print("="*70)
        print(f"📊 Link Distribution:")
        print(f"   - Seismic: {len(seismic_l1)} links")
        print(f"   - PSnow: {len(psnow_l1)} links")
        print(f"   - Learning: {len(hpelearning_l1)} links")
        print(f"   - Certification: {len(certification_l1)} links")
        print(f"   - VShow: {len(vshow_l1)} links")
        print(f"   - Total: {total_links} links")
        print("="*70 + "\n")
        
        start_time = time.time()
        
        # SEISMIC VALIDATION
        if seismic_l1:
            print(f"\n{'='*70}")
            print(f"🔍 SEISMIC VALIDATION - {len(seismic_l1)} links")
            print(f"{'='*70}")
            seismic_start = time.time()
            
            ext.check_seismic_login(driver, seis_login_link, wait, xpathlist, self.username, self.password)
            
            for idx, link in enumerate(seismic_l1, 1):
                link_start = time.time()
                print(f"\n[{idx}/{len(seismic_l1)}] {link}")
                
                Ext_seismic = ext.check_seismic_error(self.driver, wait, xpathlist, link, Errormsg)
                
                elapsed = time.time() - link_start
                if Ext_seismic:
                    errorlinks.append(link)
                    print(f"   ❌ ERROR - {elapsed:.1f}s")
                else:
                    print(f"   ✅ OK - {elapsed:.1f}s")
                
                # Show progress every 10 links
                if idx % 10 == 0:
                    progress = (idx / len(seismic_l1)) * 100
                    elapsed_total = time.time() - seismic_start
                    avg_time = elapsed_total / idx
                    remaining = (len(seismic_l1) - idx) * avg_time
                    print(f"\n   📈 Progress: {progress:.1f}% | Avg: {avg_time:.1f}s/link | ETA: {remaining/60:.1f} min")
            
            seismic_elapsed = time.time() - seismic_start
            print(f"\n{'='*70}")
            print(f"✅ Seismic Complete: {seismic_elapsed/60:.1f} minutes")
            print(f"   Errors found: {sum(1 for link in errorlinks if 'seismic' in link)}")
            print(f"{'='*70}\n")
        
        # PSNOW VALIDATION
        if psnow_l1:
            print(f"\n{'='*70}")
            print(f"🔍 PSNOW VALIDATION - {len(psnow_l1)} links")
            print(f"{'='*70}")
            psnow_start = time.time()
            
            ext.check_psnow_login(self.driver, psnow_login_link, self.wait, xpathlist, self.username, self.password)
            
            for idx, link in enumerate(psnow_l1, 1):
                link_start = time.time()
                print(f"\n[{idx}/{len(psnow_l1)}] {link}")
                
                Ext_psnow = ext.check_psnow_error(self.driver, link, wait, xpathlist, Errormsg)
                
                elapsed = time.time() - link_start
                if Ext_psnow:
                    errorlinks.append(link)
                    print(f"   ❌ ERROR - {elapsed:.1f}s")
                else:
                    print(f"   ✅ OK - {elapsed:.1f}s")
            
            psnow_elapsed = time.time() - psnow_start
            print(f"\n{'='*70}")
            print(f"✅ PSnow Complete: {psnow_elapsed/60:.1f} minutes")
            print(f"{'='*70}\n")
        
        # CERTIFICATION VALIDATION
        if certification_l1:
            print(f"\n{'='*70}")
            print(f"🔍 CERTIFICATION VALIDATION - {len(certification_l1)} links")
            print(f"{'='*70}")
            
            for idx, link in enumerate(certification_l1, 1):
                print(f"[{idx}/{len(certification_l1)}] {link}")
                Ext_certif = ext.check_certification_error(self.driver, link, Errormsg)
                if Ext_certif:
                    errorlinks.append(link)
                    print(f"   ❌ ERROR")
                else:
                    print(f"   ✅ OK")
        
        # VSHOW VALIDATION
        if vshow_l1:
            print(f"\n🔍 VSHOW VALIDATION - {len(vshow_l1)} links")
            for idx, link in enumerate(vshow_l1, 1):
                print(f"[{idx}/{len(vshow_l1)}] {link}")
                Ext_vshowval = ext.check_vs_error(self.driver, link, Errormsg)
                if Ext_vshowval:
                    errorlinks.append(link)
        
        # LEARNING VALIDATION
        if hpelearning_l1:
            print(f"\n🔍 LEARNING VALIDATION - {len(hpelearning_l1)} links")
            for idx, link in enumerate(hpelearning_l1, 1):
                print(f"[{idx}/{len(hpelearning_l1)}] {link}")
                Ext_hpelearning = ext.check_learning_error(self.driver, link, Errormsg)
                if Ext_hpelearning:
                    errorlinks.append(link)
        
        # FINAL SUMMARY
        total_elapsed = time.time() - start_time
        print(f"\n{'='*70}")
        print(f"🎉 VALIDATION COMPLETE!")
        print(f"{'='*70}")
        print(f"⏱  Total time: {total_elapsed/60:.1f} minutes")
        print(f"❌ Total errors: {len(errorlinks)}")
        print(f"✅ Total validated: {total_links}")
        print(f"{'='*70}\n")
        
                        
       
        def write_excel_report(errorlinks):
            # ✅ Use context manager
            with open(self.reverse_dict_path, 'r') as file:
                dictionary = ast.literal_eval(file.read())
            issueid = 1
            category = "invalid external links"
            account=self.username
            region=self.region
            country=self.country
            language=self.language
            Fixers =''
            Fixer_mail=''
            status = "New"
            comments = "-"
            report = []
            Domain_map = {'ma'}

            for ele in errorlinks:
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
                else:
                    length=0
                    
                if length==0:
                    req_length=len(str(ele))+1
                    ele=ele.ljust(req_length,'\n')
                    # ele=ele.ljust(req_length,'n')
                    linkele.append(dictionary[ele][-1])
                elif s_url==ele:
                    linkele.append(s_url2)
                else:
                    linkele.append(s_url)
                des ='invalid external links'
                linkele.append(ele)
                linkele.append(des)
                linkele.append(datetime.datetime.now())
                # linkele.append(Fixers)
                linkele.append(Fixer_mail)
                linkele.append(status)
                linkele.append(comments)
                report.append(linkele)
                issueid+=1        
                
                r = pd.DataFrame(report,columns=['Issue ID','Demo Account','Category','Region','Country','Language','Link','Error Link','Description','Time Identified','Mail ID','Status','Comments'])
                r.to_excel(self.report_path, index=False)  
        write_excel_report(errorlinks)   

    def tearDown(self):
        try:
            if self.browser:
                self.browser.close()
        except Exception:
            pass
        try:
            if self.pw:
                self.pw.stop()
        except Exception:
            pass
       

def run_account(account):
    try:
        # print("Into broken link module\n")
        # print(account[0])
        Firstrun = PRP(*account)
        Firstrun.setUp()
        Firstrun.external_url_validation()
        Firstrun.tearDown() 
        from playsound3 import playsound
        playsound("Sound/beep-01a.wav")
        print("Finished processing:", account[0])
    except Exception as e:
        print(f"Error while processing {account[0]}: {e}")

if __name__=='__main__':
    credentials = [
       ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'EMEA', 'Italy', 'Italian', 'distri'], 
    ]

    # Adjust max_workers based on your system capability (e.g., RAM, CPU, browser limits)
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.map(run_account, credentials)

               