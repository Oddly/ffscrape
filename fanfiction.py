#!/usr/bin/env python

from bs4 import BeautifulSoup
from seleniumbase import Driver 
import  time, os, subprocess, logging
from tqdm import tqdm
import tenacity

class GetLinks(): 

    ff_url = "https://fanfiction.net"
    home_directory = os.path.expanduser ( '~' )
    file_time = time.strftime("%Y%m%d-%H%M%S")
    debug = 0
    #logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    
    def __init__(self):
        pass 

    @tenacity.retry(stop=tenacity.stop_after_attempt(4), wait=tenacity.wait_fixed(.5),
                    after=tenacity.after_log(logging, logging.DEBUG))
    def get_soup(self, url):
        logging.debug('Getting url {}'.format(url))
        
        with Driver(undetectable=True, incognito=True, headless2=True) as driver:
            driver.get(url)

            # Put the above page in the 'page' variable.
            page = driver.page_source

            # Parse it with the BeautifulSoup library.
            soup_raw = BeautifulSoup(page, "html.parser")
            #logging.debug('soup_raw: %s', soup_raw)
            return soup_raw


    def pagecount(self, url):
        
        
        # Get the number of total pages in this fanfic
        page_count = 0 

        while page_count == 0:
            soup = self.get_soup(url)
            get_pages = soup.find_all('a')
            for item in get_pages:
                if item.get_text('href') == "Last":
                    logging.debug('href "Last": %s', item)
                    page_count = int((item.get('href').split("&p="))[1])
        logging.debug('Pages counted: {}'.format(page_count))
            
        final_link_list = []
        temp_list = []
        writeout_file = self.home_directory + "/scrapedlink-{time}.txt".format(time=self.file_time)

        if page_count == 0:
            url2 = url
            temp_list = self.get_links(url2)
            final_link_list.extend(temp_list)
        else:
            # Make sure the script gets the last page as well.
            page_count += 1
            if counter_requested == 0:
                counter = 1
            elif counter_requested != 0:
                counter = counter_requested
            pbar = tqdm(total=page_count)
            while counter != page_count:
                url2 = url+"&p="+str(counter)
                while not temp_list:
                    temp_list = self.get_links(url2)
                final_link_list.extend(temp_list)
                temp_list.clear()
                counter += 1
                pbar.update(1)
                if counter % 10 == 0:
                    self.writeout(writeout_file, final_link_list)
                    final_link_list.clear()
                    logging.debug("Written to file!")
                logging.debug('Current counter: {}'.format(counter))
            self.writeout(writeout_file, final_link_list)
            final_link_list.clear()
            pbar.close()
        
        transfer_ul_link = "https://transfer.sh/" + fanfic_name

        self.writeout(writeout_file, final_link_list)

        transfer_sh = subprocess.run(["curl", "--upload-file", writeout_file, transfer_ul_link], capture_output = True, text = True)

        logging.info('Fanfic done: %s', fanfic_name)
        logging.info('Download URL: %s', transfer_sh.stdout)

    
    def get_links(self, url):

        # Get the page source and set variables
        link_soup = self.get_soup(url)
        page_links = []
        fanfiction_links = []
        
        # Get all of the links on the page 
        fanfiction = link_soup.find_all('a', class_='stitle')
        #logging.debug('get_links find_all "a": %s', fanfiction)

        
        for item in fanfiction:
            fanfiction_links.append(item.get('href'))
        
        for link in fanfiction_links:
            logging.debug('Link appended: %s%s', self.ff_url, link)
            page_links.append(self.ff_url + link + "\n")

        return page_links

    def writeout(self, location, write_list):
        
        with open(location, "a") as of:
            of.write("".join(str(item) for item in write_list))


    def __str__(self):
        print(self.get_topics())



scraping_url = input('Give the URL to scrape please: ')
fanfic_name = input('Give the fanfic name: ')
counter_requested = int(input('Enter the starting page number (empty for 0): ') or 0)
a = GetLinks()
a.pagecount(scraping_url)
#a.pagecount("https://www.fanfiction.net/book/Heralds-of-Valdemar/?&srt=1&r=10")
