from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, StaleElementReferenceException
from selenium.common.exceptions import TimeoutException, ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.common.by import By
import time
import threading
import os

class PRP():
    def __init__(self, username: str, password: str, region: str, country: str, language: str, acc_type: str):
        self.username = username
        self.password = password
        if region == "NA":
            region = 'NAR'
        self.region = region
        self.country = country
        self.account_type = acc_type
        self.language = language
        self.base_url = "https://partner.hpe.com"
        
        # Create required directories if they don't exist
        for directory in ["Page Trees", "DocumentLinks", "Reverse Dicts", "External Urls"]:
            os.makedirs(directory, exist_ok=True)
        
        # Define file paths for storing results
        self.page_tree_path = 'Page Trees/PageTree{r}_{c}_{l}_{a}.txt'.format(
            r=self.region, c=self.country, l=self.language, a=self.account_type)
        self.doc_link_path = 'DocumentLinks/Doclinks{r}_{c}_{l}_{a}.txt'.format(
            r=self.region, c=self.country, l=self.language, a=self.account_type)
        self.reverse_dict_path = 'Reverse Dicts/RevDict{r}_{c}_{l}_{a}.txt'.format(
            r=self.region, c=self.country, l=self.language, a=self.account_type)
        self.external_urls_path = 'External Urls/External{r}_{c}_{l}_{a}.txt'.format(
            r=self.region, c=self.country, l=self.language, a=self.account_type)
        
        # Load configuration lists from files or define them inline
        self.delayed_loading_links = self.load_config_file("delayed_loading.txt", [])
        self.breadcrumblinks = self.load_config_file("breadcrumb_links.txt", [])
        self.absurd_links = self.load_config_file("absurd_links.txt", [])
        self.breadcrumb_prefix = self.load_config_file("Breadcrumb_Prefix.txt", [
            "https://partner.hpe.com/group/prp/settings-old",
            "https://partner.hpe.com/group/prp/price-communications",
            "https://partner.hpe.com/group/prp/reports"
        ])
        
        # Track specific links that we're looking for
        self.specific_links = [
            "https://partner.hpe.com/group/prp/article-display-page?id=861443016"
        ]
        
        self.prp_links = None
        self.lock = threading.Lock()
        self.driver = None

    def load_config_file(self, filename, default_list):
        """Load configuration from a file or return default if file doesn't exist"""
        try:
            with open(filename, 'r') as file:
                return [s.strip() for s in file.readlines() if s.strip()]
        except FileNotFoundError:
            print(f"Config file {filename} not found. Using default values.")
            return default_list

    def setUp(self):
        """Initialize the webdriver"""
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("--start-maximized")
        
        # Uncomment if you need headless mode
        # options.add_argument("--headless")
        # options.add_argument("--window-size=1920,1080")
        
        try:
            # Try to use the provided webdriver path
            webdriver_path = "Webdrivers/chromedriver.exe"
            service = webdriver.chrome.service.Service(webdriver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"Error with specific webdriver: {str(e)}")
            # Fall back to system webdriver
            self.driver = webdriver.Chrome(options=options)
        
        self.driver.maximize_window()
        print("Browser setup complete")

    def login(self):
        """Login to the HPE partner portal"""
        driver = self.driver
        wait = WebDriverWait(driver, 30, poll_frequency=1, 
                            ignored_exceptions=[ElementNotVisibleException, 
                                               ElementNotSelectableException, 
                                               NoSuchElementException, 
                                               StaleElementReferenceException])
        
        print(f"Logging in with account: {self.username}")
        driver.get(self.base_url)
        
        # Handle login page
        try:
            wait.until(EC.element_to_be_clickable((By.ID, "oktaEmailInput"))).send_keys(self.username)
            wait.until(EC.element_to_be_clickable((By.ID, "oktaSignInBtn"))).click()
            wait.until(EC.element_to_be_clickable((By.ID, "password-sign-in"))).send_keys(self.password)
            wait.until(EC.element_to_be_clickable((By.ID, 'onepass-submit-btn'))).click()
            print("Login credentials entered")
            
            # Wait for main page to load
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(10)  # Allow time for authentication to complete
            
            # Check login success
            if "partner.hpe.com" in driver.current_url:
                print("Login successful")
                return True
            else:
                print("Login may have failed, current URL:", driver.current_url)
                return False
        
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False

    def is_valid_url(self, url, allurls):
        """Check if a URL is valid and should be processed"""
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        if (url == '' or 
            url in allurls or 
            'login' in url or 
            'logout' in url or 
            '#' in url or 
            '?p_p_id=com' in url or
            url == 'javascript:void(0)' or 
            url == 'false'):
            return False
        
        return True

    def normalize_url(self, url):
        """Normalize URLs to a consistent format"""
        url = url.strip()
        
        # Handle relative URLs
        if not url.startswith('http'):
            if url.startswith("/"):
                if url.startswith("/group/prp"):
                    url = 'https://partner.hpe.com' + url
                else:
                    url = 'https://partner.hpe.com' + url
            else:
                if 'article-display-page?' in url or 'group/prp' in url:
                    url = 'https://partner.hpe.com/group/prp/' + url
        
        return url

    def filter_breadcrumbs(self, link):
        """Determine if a link is a breadcrumb link to be filtered out"""
        status = True
        for li in self.breadcrumb_prefix:
            if link.startswith(li):
                status = False
        if link in self.breadcrumblinks:
            status = False
        return status

    def extract_links(self, driver, link, allurls, tree_dict):
        """
        Enhanced link extraction function with improved strategies for finding links
        """
        extracted_links = []
        
        # Track whether specific links were found
        for specific_link in self.specific_links:
            if specific_link not in allurls:
                print(f"Looking for specific link: {specific_link}")
        
        # More comprehensive element selection
        try:
            # 1. Standard a href extraction
            ahref = driver.find_elements(By.TAG_NAME, "a")
            for ele in ahref:
                try:
                    url = ele.get_attribute("href")
                    if url and self.is_valid_url(url, allurls):
                        normalized_url = self.normalize_url(url)
                        if normalized_url.startswith('http'):
                            tree_dict[link].append(normalized_url)
                            extracted_links.append(normalized_url)
                            
                            # Check if we found a specific link
                            for specific_link in self.specific_links:
                                if normalized_url == specific_link:
                                    print(f"✓ Found specific link in a tag: {specific_link}")
                except Exception as e:
                    print(f"Error processing a tag: {str(e)}")
            
            # 2. Input value extraction
            inputval = driver.find_elements(By.CSS_SELECTOR, "input")
            for ele in inputval:
                try:
                    url = ele.get_attribute("value")
                    if url and self.is_valid_url(url, allurls):
                        normalized_url = self.normalize_url(url)
                        if normalized_url.startswith('http'):
                            tree_dict[link].append(normalized_url)
                            extracted_links.append(normalized_url)
                            
                            # Check if we found a specific link
                            for specific_link in self.specific_links:
                                if normalized_url == specific_link:
                                    print(f"✓ Found specific link in input value: {specific_link}")
                except Exception as e:
                    print(f"Error processing input tag: {str(e)}")
            
            # 3. Check data attributes that might contain URLs
            elements_with_data = driver.find_elements(By.CSS_SELECTOR, "[data-url], [data-href], [data-link]")
            for ele in elements_with_data:
                for attr in ['data-url', 'data-href', 'data-link']:
                    try:
                        url = ele.get_attribute(attr)
                        if url and self.is_valid_url(url, allurls):
                            normalized_url = self.normalize_url(url)
                            if normalized_url.startswith('http'):
                                tree_dict[link].append(normalized_url)
                                extracted_links.append(normalized_url)
                                
                                # Check if we found a specific link
                                for specific_link in self.specific_links:
                                    if normalized_url == specific_link:
                                        print(f"✓ Found specific link in data attribute: {specific_link}")
                    except Exception as e:
                        continue
            
            # 4. Extract URLs from onclick attributes
            onclick_elements = driver.find_elements(By.CSS_SELECTOR, "[onclick]")
            for ele in onclick_elements:
                try:
                    onclick = ele.get_attribute("onclick")
                    if onclick and ("window.location" in onclick or "window.open" in onclick):
                        # Extract URL from onclick using split by quotes
                        url_parts = onclick.split("'")
                        if len(url_parts) > 1:
                            potential_url = url_parts[1]
                            if self.is_valid_url(potential_url, allurls):
                                normalized_url = self.normalize_url(potential_url)
                                if normalized_url.startswith('http'):
                                    tree_dict[link].append(normalized_url)
                                    extracted_links.append(normalized_url)
                                    
                                    # Check if we found a specific link
                                    for specific_link in self.specific_links:
                                        if normalized_url == specific_link:
                                            print(f"✓ Found specific link in onclick: {specific_link}")
                except Exception as e:
                    continue
            
            # 5. Look for article IDs that could be constructed into URLs
            article_elements = driver.find_elements(By.CSS_SELECTOR, "[data-article-id], [data-id]")
            for ele in article_elements:
                for attr in ['data-article-id', 'data-id']:
                    try:
                        article_id = ele.get_attribute(attr)
                        if article_id:
                            constructed_url = f"https://partner.hpe.com/group/prp/article-display-page?id={article_id}"
                            if constructed_url not in allurls:
                                tree_dict[link].append(constructed_url)
                                extracted_links.append(constructed_url)
                                
                                # Check if we found a specific link
                                for specific_link in self.specific_links:
                                    if constructed_url == specific_link:
                                        print(f"✓ Found specific link via article ID: {specific_link}")
                    except Exception as e:
                        continue
            
            # 6. Extract from page source for special cases
            for specific_link in self.specific_links:
                if specific_link not in allurls and specific_link in driver.page_source:
                    print(f"✓ Found specific link in page source but not in DOM: {specific_link}")
                    tree_dict[link].append(specific_link)
                    extracted_links.append(specific_link)
            
            # 7. Extract URLs from JavaScript (more advanced)
            try:
                article_links = driver.execute_script('''
                    // Look for article IDs or links in the page's JavaScript context
                    var articleIds = [];
                    // Try to find common patterns where article IDs might be stored
                    if (typeof window.articleIds !== 'undefined') {
                        articleIds = window.articleIds;
                    } else if (typeof window.articles !== 'undefined' && Array.isArray(window.articles)) {
                        articleIds = window.articles.map(a => a.id).filter(id => id);
                    }
                    
                    // Look for links containing article-display-page
                    var links = Array.from(document.querySelectorAll('a')).map(a => a.href)
                        .filter(href => href && href.includes('article-display-page'));
                    
                    return {
                        articleIds: articleIds,
                        articleLinks: links
                    };
                ''')
                
                if article_links and isinstance(article_links, dict):
                    # Process article IDs
                    if 'articleIds' in article_links and article_links['articleIds']:
                        for article_id in article_links['articleIds']:
                            constructed_url = f"https://partner.hpe.com/group/prp/article-display-page?id={article_id}"
                            if constructed_url not in allurls:
                                tree_dict[link].append(constructed_url)
                                extracted_links.append(constructed_url)
                                
                                # Check if we found a specific link
                                for specific_link in self.specific_links:
                                    if constructed_url == specific_link:
                                        print(f"✓ Found specific link via JS articleIds: {specific_link}")
                    
                    # Process article links
                    if 'articleLinks' in article_links and article_links['articleLinks']:
                        for article_link in article_links['articleLinks']:
                            if article_link and self.is_valid_url(article_link, allurls):
                                normalized_url = self.normalize_url(article_link)
                                if normalized_url.startswith('http'):
                                    tree_dict[link].append(normalized_url)
                                    extracted_links.append(normalized_url)
                                    
                                    # Check if we found a specific link
                                    for specific_link in self.specific_links:
                                        if normalized_url == specific_link:
                                            print(f"✓ Found specific link via JS articleLinks: {specific_link}")
            except Exception as e:
                print(f"Error executing JavaScript: {str(e)}")
        
        except Exception as e:
            print(f"Error in extract_links for {link}: {str(e)}")
        
        return list(set(extracted_links))

    def scrape(self, queue, internal, external, allurls, doclinks, tree_dict):
        """Main scraping function to process the queue of URLs"""
        driver = self.driver
        wait = WebDriverWait(driver, 30, ignored_exceptions=[TimeoutException])
        
        processed_count = 0
        
        while queue:
            link = queue.pop(0).strip().strip('\n')
            processed_count += 1
            
            if processed_count % 10 == 0:
                print(f"Processed {processed_count} links. Queue size: {len(queue)}")
            
            # Skip duplicate URLs or already processed ones
            if link in allurls:
                continue
            
            # Add to all URLs immediately to prevent duplicate processing
            allurls.add(link)
            
            # Handle document links
            if ('/documents' in link or '/esm' in link or 
                link.endswith('.pdf') or link.endswith('.xlsx') or link.endswith('.zip')):
                doclinks.add(link)
                continue
            
            # Process web links
            if link.startswith('http'):
                if link.startswith("https://partner.hpe.com"):
                    tree_dict.update({link: []})
                    
                    try:
                        print(f"Navigating to: {link}")
                        driver.get(link)
                        
                        # Handle special cases for certain links
                        if link in self.delayed_loading_links or link.strip() in self.delayed_loading_links:
                            try:
                                wait.until(EC.visibility_of_all_elements_located((By.ID, 'disBtn')))
                            except TimeoutException:
                                print(f"Timeout waiting for delayed loading elements on {link}")
                                pass
                        
                        if link in self.absurd_links:
                            print(f"Waiting extra time for absurd link: {link}")
                            time.sleep(15)
                        
                        # Wait for the page to load completely
                        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                        
                        # Filter and categorize links
                        if self.filter_breadcrumbs(link):
                            internal.add(link)
                        
                        # Extract links from the page
                        new_links = self.extract_links(driver, link, allurls, tree_dict)
                        queue.extend([l for l in new_links if l not in allurls])
                        
                    except Exception as e:
                        print(f"Error processing {link}: {str(e)}")
                
                else:
                    # Handle external links
                    if self.filter_breadcrumbs(link):
                        external.add(link)
            
            # Remove duplicates from queue
            queue = list(set(queue))
        
        return allurls, internal, external, doclinks, tree_dict

    def reverse_dict_builder(self, treedict, allurls):
        """Build a reverse dictionary mapping URLs to their sources"""
        print("Building reverse dictionary...")
        keys = list(treedict.keys())
        values = list(treedict.values())
        revdict = {}
        
        for url in allurls:
            sources = []
            for i, links in enumerate(values):
                if url in links:
                    sources.append(keys[i])
            
            if sources:
                revdict[url] = sources
        
        return revdict

    def run(self):
        """Main function to run the scraper"""
        try:
            print(f"Starting scraper for {self.region} - {self.country} - {self.language} - {self.account_type}")
            self.setUp()
            
            if not self.login():
                print("Login failed. Aborting.")
                self.tearDown()
                return False
            
            internal = set()
            external = set()
            docs = set()
            all_links = set()
            tree_dict = {}

            # 1st Pass: Start with the specific link
            queue = ["https://partner.hpe.com/group/prp/article-display-page?id=861443016"]
            print("Starting with specific missing link...")
            all_links, internal, external, docs, tree_dict = self.scrape(
                queue, internal, external, all_links, docs, tree_dict
            )
            
            # Start with the base URL
            queue = [self.base_url]
            
            print("Beginning link extraction...")
            all_links, internal, external, docs, tree_dict = self.scrape(
                queue, internal, external, all_links, docs, tree_dict)
            
            # Save the results
            self._save_results(internal, external, docs, all_links, tree_dict)
            
            # Log summary
            self.prp_links = len(internal) + len(all_links) + len(external) + len(docs)
            print(f"Scraping completed. Found {len(internal)} internal links, {len(external)} external links, {len(docs)} document links.")
            print(f"Total links processed: {self.prp_links}")
            
            # Check if specific links were found
            for specific_link in self.specific_links:
                if specific_link in all_links:
                    print(f"✓ Specific link was found and saved: {specific_link}")
                else:
                    print(f"✗ Specific link was NOT found: {specific_link}")
            
            return True
            
        except Exception as e:
            print(f"Error in run method: {str(e)}")
            return False
        
        finally:
            self.tearDown()

    def _save_results(self, internal, external, docs, all_links, tree_dict):
        """Save the scraped results to files"""
        print("Saving results to files...")
        
        # Save internal links
        with open(self.page_tree_path, 'w') as filehandle:
            for item in internal:
                if item.startswith("https://partner.hpe.com/group/prp"):
                    filehandle.write('%s\n' % item)
        
        # Save external links
        with open(self.external_urls_path, 'w') as filehandle:
            for item in external:
                filehandle.write('%s\n' % item)
        
        # Save document links
        with open(self.doc_link_path, 'w') as filehandle:
            for item in docs:
                filehandle.write('%s\n' % item)
        
        # Build and save reverse dictionary
        revdict = self.reverse_dict_builder(tree_dict, all_links)
        with open(self.reverse_dict_path, 'w') as filehandle:
            filehandle.write(str(revdict))
        
        print("All results saved successfully")

    def tearDown(self):
        """Clean up resources"""
        if self.driver:
            print("Closing browser")
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Error closing browser: {str(e)}")


def main():
    """Main function to run the scraper with the specified credentials"""
    credentials = [
        # Format: [username, password, region, country, language, account_type]
        ['demo_french_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'France', 'French', 'Distri']
        
        # Add other credentials as needed
        # ['demo_na_proximity@pproap.com', 'Login2PRP!', 'NA', 'USA', 'English', 'CTDB'],
        # ['demo_italian_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Italy', 'Italian', 'Distri'],
        # ...
    ]
    
    for acc in credentials:
        print(f"\n{'='*50}")
        print(f"Starting scraping for account: {acc[0]}")
        print(f"{'='*50}\n")
        
        scraper = PRP(acc[0], acc[1], acc[2], acc[3], acc[4], acc[5])
        success = scraper.run()
        
        if success:
            print(f"Successfully completed scraping for {acc[0]}")
        else:
            print(f"Failed to complete scraping for {acc[0]}")
        
        print(f"\n{'='*50}")
        print(f"Completed {acc[0]}")
        print(f"{'='*50}\n")


if __name__ == '__main__':
    main()