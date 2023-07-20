#!/usr/bin/env python

from bs4 import BeautifulSoup
#import undetected_chromedriver as uc
from seleniumbase import DriverContext 
import itertools, time, random, os, subprocess
from tqdm import tqdm

class GetLinks(): 

    ff_url = "https://fanfiction.net"
    soup_cache = dict()
    home_directory = os.path.expanduser ( '~' )
    file_time = time.strftime("%Y%m%d-%H%M%S")
    debug = 0
    
    def __init__(self):
        pass 

    def get_soup(self, url, cache_on=False):

        soup_cache = self.soup_cache

        if self.debug == 1:
            print("url: "+url)

        # Check whether we have the URL in cache
        if url not in soup_cache:

            if self.debug == 1:
                # DEBUG
                print("Cache MISS...requesting")
            
           # # Use undetected_chromedriver to bypass Cloudflare.
           # chrome_options = uc.ChromeOptions()
           # #chrome_options.add_argument("--user-data-dir=/tmp/google/chrome/user/data"); 
           # chrome_options.add_argument("--incognito");
           # chrome_options.add_argument("--disable-extensions");
           # chrome_options.add_argument("--disable-application-cache");
           # chrome_options.add_argument("--disable-setuid-sandbox");
           # chrome_options.add_argument("--headless=new");
           # chrome_options.add_argument("--no-sandbox");
           # chrome_options.add_argument("--disable-dev-shm-usage");
           # chrome_options.add_argument("--disable-browser-side-navigation");
           # chrome_options.add_argument("--disable-gpu");
           # driver = uc.Chrome(headless=True,use_subprocess=False,options=chrome_options)
           # driver.get(url)
             
            # Sleep a random time 0..15 as not to trigger anti-spam.
            #time.sleep(random.randint(0,15))
            with DriverContext(uc=True, incognito=True) as driver:
                driver.get(url)
                # Put the above page in the 'page' variable.
                page = driver.page_source

                # Put results in "soup_cache" if cached is requested.
                if cache_on == True:

                    if self.debug == 1:
                        # DEBUG
                        print("Result to the cache!")
                
                    # Parse it with the BeautifulSoup library.
                    soup_cache[url] = BeautifulSoup(page, "html.parser")
                    soup_raw = soup_cache[url]

                # Skip "soup_cache" if caching is not requested.
                elif cache_on == False:

                    if self.debug == 1:
                        # DEBUG
                        print("Result not to the cache!")

                    # Parse it with the BeautifulSoup library.
                    soup_raw = BeautifulSoup(page, "html.parser")
                driver.quit()
                return soup_raw
        else:
            if self.debug == 1:
                # DEBUG
                print('Cache HIT...not requesting.')
            return soup_cache[url]

    def pagecount(self, url):
        
        soup = self.get_soup(url, cache_on=True)
        
        # Get the number of total pages in this fanfic
        page_count = int() 
        get_pages = soup.find_all('a')
        for item in get_pages:
            if item.get_text('href') == "Last":
                page_count = int((item.get('href').split("&p="))[1])
        if self.debug == 0:
            # DEBUG
            print("page count=",page_count)

        final_link_list = []

        if page_count == 0:
            url2 = url
            temp_list = self.get_links(url2)
            final_link_list.extend(temp_list)
        else:
            # Make sure the script gets the last page as well.
            page_count += 1
            counter = 1
            pbar = tqdm(total=page_count)
            while counter != page_count:
                url2 = url+"&p="+str(counter)
                temp_list = self.get_links(url2)
                final_link_list.extend(temp_list)
                temp_list.clear()
                counter += 1
                pbar.update(1)
                if self.debug == 1:
                    print(counter)
            pbar.close()
        
        writeout_file = self.home_directory + "/scrapedlink-{time}.txt".format(time=self.file_time)
        transfer_ul_link = "https://transfer.sh/" + fanfic_name

        with open(writeout_file, "a") as of:
            of.write("".join(str(item) for item in final_link_list))

        transfer_sh = subprocess.run(["curl", "--upload-file", writeout_file, transfer_ul_link], capture_output = True, text = True)

        print("Fanfic done: %s" %(fanfic_name))
        print("Download URL: %s" %(transfer_sh.stdout))

    
    def get_links(self, url):

        # Get the page source and set variables
        link_soup = self.get_soup(url, cache_on=False)
        page_links = []
        fanfiction_links = []
        
        # Get all of the links on the page 
        fanfiction = link_soup.find_all('a', class_='stitle')

        
        for item in fanfiction:
            fanfiction_links.append(item.get('href'))
        
        for link in fanfiction_links:
            if self.debug == 1:
                print(self.ff_url+link)
            page_links.append(self.ff_url + link + "\n")

        return page_links


    def __str__(self):
        print(self.get_topics())



scraping_url = input('Give the URL to scrape please: ')
fanfic_name = input('Give the fanfic name: ')
a = GetLinks()
a.pagecount(scraping_url)
#a.pagecount("https://www.fanfiction.net/book/Heralds-of-Valdemar/?&srt=1&r=10")
