from bs4 import BeautifulSoup

def emptypagecheck(link, phrase, default_phrase, soup):
    try:
        phrase_caught = soup.find(id="main-content").get_text()
    except:
        phrase_caught = ''

    if phrase_caught != '':
        content = phrase_caught.splitlines()

        for i in range(len(content)):
            content[i] = " ".join(content[i].split())
        content = [line for line in content if line]

        if len(content) == 3:
            if content[0] == phrase or content[0] == default_phrase:
                return link
        elif len(content) == 0:
            return link

    return ''
  
            
        
        
     
           
    
        

# credentials=VaultSample.result
#credentials = [['demo_indonesian_distributor@pproap.com', 'ExperiencePRP!', 'APJ', 'Indonesia', 'Indonesian', 'Distri']]
# credentials = [['demo_hpelarptbr_01@pproap.com','ExperiencePRP!','LAR','Brazil','Portugese','T2'],['demo_korean_kr_t2solutionprovider@pproap.com','ExperiencePRP!','APJ','Korea','Korean','T2'],
# ['demo_distributor_lar@pproap.com', 'ExperiencePRP!', 'LAR', 'Brazil', 'Portugese', 'CTD']]
# for acc in credentials:
#     print("into empty page module\n")
#     Firstrun=PRP(acc[0],acc[1],acc[2],acc[3],acc[4],acc[5])
#     Firstrun.setUp()
#     Firstrun.test_empty_page()
#     Firstrun.tearDown()
#     print("going into the next account")














