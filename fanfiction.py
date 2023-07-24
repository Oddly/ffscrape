#!/usr/bin/env python

from bs4 import BeautifulSoup
from seleniumbase import Driver 
import  time, os, subprocess
from tqdm import tqdm
from tenacity import retry

class GetLinks(): 

    ff_url = "https://fanfiction.net"
    home_directory = os.path.expanduser ( '~' )
    file_time = time.strftime("%Y%m%d-%H%M%S")
    debug = 0
    
    def __init__(self):
        pass 

    @retry()
    def get_soup(self, url):

        if self.debug == 1:
            print("url: "+url)

        with Driver(undetectable=True, incognito=True, headless2=True) as driver:
            
            driver.get(url)

            # Put the above page in the 'page' variable.
            page = driver.page_source

            # Parse it with the BeautifulSoup library.
            soup_raw = BeautifulSoup(page, "html.parser")
            return soup_raw


    def pagecount(self, url):
        
        soup = self.get_soup(url)
        
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
        writeout_file = self.home_directory + "/scrapedlink-{time}.txt".format(time=self.file_time)

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
                if counter % 10 == 0:
                    self.writeout(writeout_file, final_link_list)
                    final_link_list.clear()
                    print("Written to file!")
                if self.debug == 1:
                    print(counter)
            pbar.close()
        
        transfer_ul_link = "https://transfer.sh/" + fanfic_name

        self.writeout(writeout_file, final_link_list)

        transfer_sh = subprocess.run(["curl", "--upload-file", writeout_file, transfer_ul_link], capture_output = True, text = True)

        print("Fanfic done: %s" %(fanfic_name))
        print("Download URL: %s" %(transfer_sh.stdout))

    
    def get_links(self, url):

        # Get the page source and set variables
        link_soup = self.get_soup(url)
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

    def writeout(self, location, write_list):
        
        with open(location, "a") as of:
            of.write("".join(str(item) for item in write_list))


    def __str__(self):
        print(self.get_topics())



scraping_url = input('Give the URL to scrape please: ')
fanfic_name = input('Give the fanfic name: ')
a = GetLinks()
a.pagecount(scraping_url)
#a.pagecount("https://www.fanfiction.net/book/Heralds-of-Valdemar/?&srt=1&r=10")
