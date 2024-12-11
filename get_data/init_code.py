import requests
from bs4 import BeautifulSoup
import os
from tqdm import tqdm
import threading
import logging

from funct.functs import delete_folder 
from extract_article import read_pdf_with_formatting



BASE_URL = "https://www.legifrance.gouv.fr"
# Get the absolute path where the Python script is located
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))  # this file path
DATA_PATH = os.path.join(SCRIPT_PATH, 'data/all_data') # main & global data path
#ARTICLE_PATH = os.path.join(DATA_PATH, 'legiArticles') # folder for artcile for each code
MAX_WORKER = 5 # work on MAX_WORKER pdf files to exctract articles at the same times


# Configure logging
log_file_path = os.path.join(SCRIPT_PATH, 'data/log/error_log_code.txt')
# Erase previous log content by opening in write mode
with open(log_file_path, 'w') as log_file:
    pass 
logging.basicConfig(
    filename=os.path.join(log_file_path),  # Name of the log file
    level=logging.ERROR,       # Log level to capture errors and above
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format of log messages
)



def getPDF(index, output_path='data/code_pdf'):
    # Step 1: Fetch the webpage content
    url = f"https://www.legifrance.gouv.fr/liste/code?etatTexte=VIGUEUR&etatTexte=VIGUEUR_DIFF&page={index}#code"
    response = requests.get(url, verify=True)
    if response.status_code == 200:
        # Step 2: Parse the webpage with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Step 3: Find the specific link
        pdf_link_tags = soup.find_all('a', {
            'target': '_blank', 
            'rel': 'noopener noreferrer nofollow',
            'href': lambda x: x and x.startswith('/download/pdf/legiOrKali')
        })

        infos = soup.find_all('p', class_= 'code-info')
        assert len(infos) == len(pdf_link_tags)

        if len(pdf_link_tags) == 0:
            return None # no data to download
        
        print('-'*100)
        print(f'Scrap code en vigueur - {url}')
        base_output_file = os.path.join(SCRIPT_PATH, output_path)
        delete_folder(base_output_file)
        codes = {}
        process = []
        for i  in tqdm(range(len(pdf_link_tags))):
            pdf_url = BASE_URL + pdf_link_tags[i]['href']
            # create code information
            code_title = pdf_url.split('=')[-1].replace('\n', '').strip()
            if code_title not in process:
                process.append(code_title)

            # get all articles of current code 
            pdf_response = requests.get(pdf_url)   
            if pdf_response.status_code == 200:
                soup = BeautifulSoup(pdf_response.text, 'html.parser')
                download_link_tag = soup.find('a', class_='doc-download')
                if download_link_tag:
                    # Extract the relative URL from the 'href' attribute
                    relative_pdf_link = download_link_tag['href']
                    pdf_url = BASE_URL + relative_pdf_link
                    response = requests.get(pdf_url)
                    # Check if the response status is OK
                    if response.status_code == 200:
                        # Save the content as a PDF
                        output_file = os.path.join(base_output_file, code_title + '.pdf')
                        with open(output_file, 'wb') as file:
                            file.write(response.content)
                        codes[output_file] = code_title
                        #print(f"PDF downloaded successfully as '{output_file}'.")
                    else:
                        logging.error(f"Failed to download PDF {pdf_url}. Status code: {response.status_code}", exc_info=True)
                else:
                    logging.error(f"Failed to load PDF page {pdf_url}. Status code: {response.status_code}", exc_info=True)
                  
            
            
                    
    else:
        #print(f"Failed to fetch the webpage. Status code: {response.status_code}")
        logging.error(f"Failed to fetch the webpage. Status code: {response.status_code}", exc_info=True)
        return None
    
    
    # Create a thread for each chunk
    all_info = []
    for i in range(0, len(list(codes.keys())), MAX_WORKER):
        # Slice the list to get a chunk of `step` elements
        chunk = list(codes.keys())[i:i+MAX_WORKER]
        infos = {}
        threads = []
        for k in chunk:
            infos[k] = {'path' : '', 'total' : 0}
            thread = threading.Thread(target=read_pdf_with_formatting, args=(k, codes[k], infos[k],))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        for k in chunk:
            all_info.append(infos[k])
        
       
           
   

    delete_folder(base_output_file)
    print('-'*100)
    return all_info

def getCodeData(output_path_pdf='data/code_pdf'):
    start_index = 1
    all_info = []
    while True:
        info = getPDF(index=start_index, output_path=output_path_pdf)
        if not info:
            return all_info
        all_info += info 
        start_index += 1
    



