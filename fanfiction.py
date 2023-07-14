#!/usr/bin/python3

from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import itertools, time, random

class GetLinks(): 

    ff_url = "https://fanfiction.net"
    soup_cache = dict()

    def __init__(self):
        pass 

    def get_soup(self, url, cache_on=False):

        soup_cache = self.soup_cache

        # DEBUG
        #print("url: "+url)

        # Check whether we have the URL in cache
        if url not in soup_cache:

            # DEBUG
            #print("Cache MISS...requesting")
            
            # Use undetected_chromedriver to bypass Cloudflare.
            driver = uc.Chrome(headless=True,use_subprocess=False)
            driver.get(url)
             
            # Sleep a random time 0..5 as not to trigger anti-spam.
            time.sleep(random.randint(0,15))

            # Put the above page in the 'page' variable.
            page = driver.page_source

            # Put results in "soup_cache" if cached is requested.
            if cache_on == True:

                # DEBUG
                # print("Result to the cache!")
            
                # Parse it with the BeautifulSoup library.
                soup_cache[url] = BeautifulSoup(page, "html.parser")
                soup_raw = soup_cache[url]

            # Skip "soup_cache" if caching is not requested.
            elif cache_on == False:

                # DEBUG
                # print("Result not to the cache!")

                # Parse it with the BeautifulSoup library.
                soup_raw = BeautifulSoup(page, "html.parser")

            return soup_raw
        else:
            # DEBUG
            #print('Cache HIT...not requesting.')
            return soup_cache[url]

    def pagecount(self, url):
        
        soup = self.get_soup(url, cache_on=True)
        
        # Get the number of total pages in this fanfic
        page_count = int() 
        get_pages = soup.find_all('a')
        for item in get_pages:
            if item.get_text('href') == "Last":
                page_count = int((item.get('href').split("&p="))[1])
        # DEBUG
        # print("page count=",page_count)

        if page_count == 0:
            url2 = url
            get_links(url2)
        else:
            # Make sure the script gets the last page as well.
            page_count += 1
            counter = 1
            while counter != page_count:
                url2 = url+"&p="+str(counter)
                self.get_links(url2)
                counter += 1
    
    def get_links(self, url):

        link_soup = self.get_soup(url, cache_on=False)
        
        # Get all of the links on the page 
        fanfiction = link_soup.find_all('a', class_='stitle')

        fanfiction_links = []
        for item in fanfiction:
            fanfiction_links.append(item.get('href'))
        
        for link in fanfiction_links:
            print(self.ff_url+link)


    def get_topics(self, topic):
    
        # Get the soup, with caching enabled.
        soup = self.get_soup(self.ff_url, cache_on=True) 

        # Get all of the topics, in Fanfiction as well as Crossovers.
        fanfiction = soup.find_all("table", id="gui_table1i")
        crossovers = soup.find_all("table", id="gui_table2i")
    
        # Put all topic text in a list. E.g: "Books"
        topic_text = []
        for item in itertools.chain(fanfiction[0].find_all('a'), crossovers[0].find_all('a')):
            topic_text.append(item.get_text('href'))
    
        # Put all the topic URLs in a list. E.g.: "/books/"
        topic_urls = []
        for item in itertools.chain(fanfiction[0].find_all('a'), crossovers[0].find_all('a')):
            topic_urls.append(item.get('href'))
    
        # Make a dictionary from both lists.
        topic_tuple = [(key.lower(), value.lower())
                       for i, (key, value) in enumerate(zip(topic_text, topic_urls))]
        topic_dict = dict(topic_tuple)
        
        # Use the class input to lookup the requested value.
        requested_topic = ""
        requested_topic = topic_dict[topic]
        print("Topic: "+requested_topic)
        return requested_topic

#    def get_stories(self):


#    def get_fanfic(self):
    
    
    def __str__(self):
        print(self.get_topics())

a = GetLinks()
a.pagecount("https://www.fanfiction.net/movie/X-Men-The-Movie/?&srt=1&lan=1&r=10&_v1=523&p=1")
#a.pagecount("https://www.fanfiction.net/book/Heralds-of-Valdemar/?&srt=1&r=10")
