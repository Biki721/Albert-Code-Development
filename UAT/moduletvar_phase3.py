
import datetime
import re
import pandas as pd
import work_phase_3 as work
import ast

class PRP():
    base_url="https://partner.hpe.com"
    webdriver_path="Webdrivers\\chromedriver.exe"
    def __init__(self, username: str,password: str,region:str,country,language,acc_type):
        self.username=username
        self.password=password
        if (region=="NA"):
            region = "NAR"
        self.region=region
        self.country=country
        self.account_type=acc_type
        self.language=language
        self.document_links='DocumentLinks\\Doclinks{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.reverse_dict_path='Reverse Dicts\\RevDict{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.page_tree_path='Page Trees\\PageTree{r}_{c}_{l}_{a}.txt'.format(r=self.region,a=self.account_type,l=self.language,c=self.country)
        self.report_path='Reports\\Tvar_Check_{r}_{c}_{l}_{a}.xlsx'.format(r=self.region,a=self.account_type,l=self.language,c=self.country)
        self.aruba_links_path = 'Aruba Urls\\Aruba{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        
    

    def test_tvar_check(self): 
        
        def tvar_check(link):
          
            #doc_types=['.pdf','.xlsx','.doc','.docx','.odt','.txt','.exe','.docm','.xml','.zip','.tar.gz']
    
            if re.search(r'\?t=',link): 
                    return link
            return ''
        def call_tvar_check():
            with open(self.document_links, "r", encoding="utf-8") as f:
                all_links = f.read().splitlines()
            output = []
            for link in all_links:
                match = tvar_check(link)
                if match:
                    output.append(match)
            # De-duplicate while preserving order
            output = list(dict.fromkeys(output))
            write_excel(output)

            return
        def write_excel(errors):
            with open(self.reverse_dict_path, "r", encoding="utf-8") as f:
                dictstr = f.read()
            mega_dict = ast.literal_eval(dictstr)

            linkele = []
            for ele in errors:
                #print(ele)
                if ele in mega_dict:
                            length=len(mega_dict[ele])
                            if length> 0:
                                s_url=mega_dict[ele][-1]
                                s_url2=mega_dict[ele][0]
                elif ele.strip() in mega_dict:
                            length=len(mega_dict[ele.strip()])
                            if length>0:
                                s_url=mega_dict[ele.strip()][-1]
                                s_url2=mega_dict[ele.strip()][0]
                else:
                    length=0
                    
                if length==0:
                    req_length = len(str(ele)) + 1
                    ele = ele.ljust(req_length,'\n')
                    # ele=ele.ljust(req_length,'n')
                    try:
                        linkele.append(mega_dict[ele][-1])
                    except KeyError:
                        linkele.append(ele.strip())
                elif s_url==ele:
                    linkele.append(s_url2)
                else:
                    linkele.append(s_url)
            account=self.username
            region = self.region
            country=self.country
            language=self.language
            issueid = [i+1 for i in range(len(errors))]
            category = ["?t variable"]*len(errors)
            status = ["New"]*len(errors)
            comments = ["-"]*len(errors)
            description = ["Tvar"]*len(errors)
            time = [datetime.datetime.now()]*len(errors)
            result = {'Issue ID':issueid,'Demo Account': account,'Category':category,'Link':linkele,'Error Link':errors,'Description':description,'Time Identified':time,'Region':region,'Country':country,'Language':language,'Mail ID':"none",'Status':status,'Comments':comments}
            df = pd.DataFrame.from_dict(result)
            df.to_excel(self.report_path)
            return
        
        #self.test_load_home_page()
        call_tvar_check()
                
        
    def tearDown(self):
        #self.driver.close()
        try:
            df = pd.read_excel(self.report_path)
        except FileNotFoundError:
            return
        if len(df)>0:
            work.work_alloc_execute(self.report_path,'Fixers_list.xlsx',self.aruba_links_path)


if __name__ == '__main__':
    credentials=[['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'EMEA', 'Turkey', 'Turkish', 'T2']]
    for acc in credentials:
        print("Tvar module")
        Firstrun=PRP(acc[0],acc[1],acc[2],acc[3],acc[4],acc[5])
        #Firstrun.setUp()
        Firstrun.test_tvar_check()
        Firstrun.tearDown()