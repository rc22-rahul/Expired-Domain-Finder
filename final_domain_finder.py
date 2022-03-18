
!pip3 install colorama
!pip3 install requests_html
!pip3 install whois-api
from requests_html import HTMLSession
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama
import lxml
import requests
import sys
import time
from whoisapi import *
import cv2

# init the colorama module
colorama.init()

GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.CYAN
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW

# initialize the set of links (unique links)
internal_urls = set()
external_urls = set()

total_urls_visited = 0



def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme == 'https' or parsed.scheme == 'http')




# init the colorama module
colorama.init()

GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.CYAN
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW

# initialize the set of links (unique links)
internal_urls = set()
external_urls = set()

total_urls_visited = 0


# headerss={"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 GTB7.1 (.NET CLR 3.5.30729)", "Referer": "http://example.com"}
headerss = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}


def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme == 'https' or parsed.scheme == 'http')


def get_all_website_links(url):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    flag = True
    urls = set()
    # domain name of the URL without the protocol
    domain_name = (urlparse(url).netloc).replace('www.','')
    # initialize an HTTP session
    session = HTMLSession()
    # make HTTP request & retrieve response
    try:
        response = session.get(url,headers=headerss,timeout=30)      
    except:      
        try:
            time.sleep(5)
            response = session.get(url,timeout=30,allow_redirects=False)
#             print(response)
        except:
            print('No response from the website')
    #         print('not availble')
    #         sys.exit(1)
            flag = False
    # execute Javascript
    try:
        response.html.render()
    except:
#         print('rendor error')
        pass
    if flag:
        try:
            soup = BeautifulSoup(response.html.html, "lxml")
        except:
            soup = BeautifulSoup(response.text,'lxml')
        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                # href empty tag
                continue
            # join the URL if it's relative (not absolute link)
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            # remove URL GET parameters, URL fragments, etc.
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not is_valid(href):
                # not a valid URL
                continue
            if href in internal_urls:
                # already in the set
                continue
            if domain_name not in href:
                # external link
                if href not in external_urls:
                    print(f"{GRAY}[!] External link: {href}{RESET}")
                    external_urls.add(href)
                continue
            print(f"{GREEN}[*] Internal link: {href}{RESET}")
            urls.add(href)
            internal_urls.add(href)
        try:
            response.close()
        except:
            pass
        try:
            session.close()
        except:
            pass
        return urls
    

def crawl(url, max_urls=2000):
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls` global set variables.
    params:
        max_urls (int): number of max urls to crawl, default is 30.
    """
    global total_urls_visited
    total_urls_visited += 1
    print(f"{YELLOW}[*] Crawling: {url}{RESET}")
    links = get_all_website_links(url)
    if links!=None:
        for link in links:
    #         print(link)
            print(total_urls_visited)
            if total_urls_visited > max_urls:
                break   
            crawl(link, max_urls=max_urls)

website_to_crawl = input('Enter the website to crawl separated by space : ').strip().split()
max_urls_to_crawl = int(input('Enter the number of crawl for each website : '))


t1 = time.perf_counter()
print(t1)

for website in website_to_crawl:
    total_urls_visited=0
    crawl(website,max_urls = max_urls_to_crawl)
    
t2 = time.perf_counter()
print(t2)

print('Total time took for excecution',t2-t1)

updated_external_domain = []
for i in external_urls:
    updated_external_domain.append((urlparse(i).netloc).replace('www.',''))
updated_external_domain = list(set(updated_external_domain))
print(len(updated_external_domain))

for _ in updated_external_domain:
  print(_)

keys_list = ['Add list of Api keys']

available = []
unavailable = []
def expired_domain_finder(domains,keys):
    try:
        for index,url in enumerate(domains):
            for key_value in keys:
                try:
                    client = Client(api_key=key_value)
                    params = RequestParameters(ignore_raw_texts=1, da=2)
                    whois = client.data(url,params)
                    print(index,'-->', url, '-------', whois.domain_availability_raw)
                        # print(whois)
                    if whois.domain_availability_raw == 'AVAILABLE':
                        available.append(url)
                        print('-------------------------------------------------------------')
                    else:
                        unavailable.append(url)
                except:
                    # print(f'The limit of over of this {key_value} so switching to next')
                    continue
                else:
                    # print('last used api key is ', key_value)
                    # print('getting out of loop')
                    break
                  

    finally:
        print('Last Api key used is : ',key_value)
        
 expired_domain_finder(updated_external_domain,keys_list)

 if len(available)==0:
    print('There are no availabe expired domains for use')
else:
    print('Here is the list of available expired domains')
    for _ in available:
        print(_)
        
        
string = ''
for _ in website_to_crawl:
    string+=urlparse(_).netloc.replace('www.',' ')
    
with open(f"unvailable domain({string}).txt",'w+') as f:
    for _ in unavailable:
#         print(_.strip())
        print(_.strip(),file = f)
    
 with open(f"external_links({string}).txt", "w") as f:
    for external_link in external_urls:
        print(external_link.strip(), file=f)
  
with open(f"available domain({string}).txt",'w+') as f:
    for _ in available:
        # print(_.strip())
        print(_.strip(),file = f)
        
        
        
        
        

                  
            
        
        
        
        
