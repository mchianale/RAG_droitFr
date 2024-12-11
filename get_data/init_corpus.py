import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
import threading

from funct.getWikiInfo import get_wikipedia_info_from_url

BASE_URL = "https://fr.wikipedia.org/wiki/"
# Get the absolute path where the Python script is located
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))  # this file path
DATA_PATH = os.path.join(SCRIPT_PATH, 'data/all_data') # main & global data path
#DEF_PATH = os.path.join(DATA_PATH, 'wikiCorpus')




def get_article_links(base_root, already_article_links=[], max_workers=20):
    base_root = base_root.replace(' ', '_').lower()
    base_root = base_root[0].upper() + base_root[1:]
    base_url = f"https://fr.wikipedia.org/wiki/Cat%C3%A9gorie:Portail:{base_root}/Articles_li%C3%A9s"
    current_url = base_url
    total_count = None
    current_articles, threads = [], []
    output_paths = [os.path.join(DATA_PATH, f"{base_root}{i}.json") for i in range(max_workers)]
    output_files = [open(output_path, 'w') for output_path in output_paths]
    files_info = [{'path' : output_path, 'total' : 0} for output_path in output_paths]
    for output_file in output_files:
        output_file.write('[\n')
    firsts = [{'first' : True} for output_path in output_paths]
   
    while current_url:
        #print(f"Fetching: {current_url}")
        response = requests.get(current_url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract total page count on the first iteration
        if total_count is None:
            total_info = soup.select_one('div#mw-pages p')
            if total_info:
                text = total_info.text.split(',')[0]
                # Extract total number of pages using string parsing
                total_count = int("".join(filter(str.isdigit, text)))
                progress_bar = tqdm(total=total_count, desc=f"Retrieve link article for {base_root}", unit="step")
        
        # Extract links to articles
        subsoup = soup.select('div.mw-category-columns')
        for column in subsoup:
            for link in column.select('div.mw-category a'):
                href = link.get('href')
                if href and href.startswith("/wiki/"):
                    full_url = f"https://fr.wikipedia.org{href}"
                    if full_url not in already_article_links:
                        already_article_links.append(full_url)
                        current_articles.append(full_url)
                        if len(current_articles) == max_workers:
                            for i, full_url_ in enumerate(current_articles):
                                thread = threading.Thread(target=get_wikipedia_info_from_url, args=(full_url_, output_files[i], firsts[i], files_info[i],))
                                thread.start()
                                threads.append(thread)
                            for thread in threads:
                                thread.join()
                                progress_bar.update(1)          
                            current_articles, threads = [], []
                            

        # Find the "next page" link
        next_page = soup.find('a', string="page suivante")
        if next_page:
            next_url = next_page.get('href')
            current_url = f"https://fr.wikipedia.org{next_url}"
        else:
            current_url = None

    for i, full_url_ in enumerate(current_articles):
        thread = threading.Thread(target=get_wikipedia_info_from_url, args=(full_url_, output_files[i], firsts[i], files_info[i],))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
        progress_bar.update(1)    

    for output_file in output_files:
        output_file.write('\n]')
        output_file.close()

    progress_bar.close()
    t = 0
    for i in files_info:
        t += i['total']
    return files_info, already_article_links

 

