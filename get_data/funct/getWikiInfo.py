import wikipediaapi
import urllib.parse
import json 
import logging
import os 
import requests
from bs4 import BeautifulSoup

# Configure logging
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))  # this file path
log_file_path = os.path.join(SCRIPT_PATH, 'error_log_wiki.txt')
# Erase previous log content by opening in write mode
with open(log_file_path, 'w') as log_file:
    pass 

logging.basicConfig(
    filename=os.path.join(log_file_path),  # Name of the log file
    level=logging.ERROR,       # Log level to capture errors and above
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format of log messages
    force=True
)

def get_wikipedia_info_from_url(url,output_file, first, file_info, lang='fr'):
    try:
        # Initialize the Wikipedia API with the specified language
        wiki_wiki = wikipediaapi.Wikipedia('rag_law_fr', lang)

        # Extract the page title from the URL
        """parsed_url = urlparse(url)
        if parsed_url.netloc != "fr.wikipedia.org" or not parsed_url.path.startswith("/wiki/"):
            raise ValueError("The URL is not a valid French Wikipedia article URL.")"""
        
        page_title = urllib.parse.unquote(url.split('https://fr.wikipedia.org/wiki/')[1].replace('_', ' '))
        
        if not page_title:
            logging.error(f"No valid page title could be extracted from the {url}.")
            return 
        
        # Fetch the page using the extracted title
        page = wiki_wiki.page(page_title)

        # Check if the page exists
        if not page.exists():
            #result['error'] = "The page does not exist."
            logging.error(f"The page '{page_title}' does not exist for {url}.")
            return 

        # Get the summary and content of the page
        summary = page.summary
        #content = page.text

        # Extract sections and links
        """sections = page.sections
        related_articles = {
            title: title.replace(" ", "_")
            for title in page.links.keys()
        }"""

        result = {}
        result['url'] = page.fullurl
        result['text'] = summary
        #result['content'] = content
        #result['sections'] = [section.title for section in sections]
        #result['related_articles'] = related_articles
        file_info['total'] += 1
        if result['text'] == "":
            logging.exception(f"empty text while processing the {url}.")
        if not first['first']:
            output_file.write(',\n')
        json.dump(result, output_file)
        del result
        first['first'] = False
       
    except:
        headers = {
            "User-Agent": "rag_law_fr",  # User-Agent for identification
        }
        # Send the GET request with headers
        response = requests.get(url, headers=headers)
        # Check the response status code
        if response.status_code == 200:
            # Decode the JSON data into a dictionary: json_data
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find the div with the class 'mw-content-ltr'
            content_div = soup.find("div", class_="mw-content-ltr")
            
            if content_div:
                # Get all the elements (p, ul, li, etc.) before any div with class 'mw-heading'
                elements_before_heading = []
                
                for element in content_div.find_all(["p", "ul", "li"], recursive=False):
                    # Check if the next element is a heading div (mw-heading)
            
                    next_sibling = element.find_next_sibling()
                    if next_sibling and next_sibling.name == "div" and "mw-heading" in next_sibling.get("class", []):
                        break

                    for b_tag in element.find_all("b"):
                        b_tag.insert_before(' ')  # Insert space before <b> tag
                        b_tag.unwrap()  # Remove the <b> tag but keep its content
                    
                    elements_before_heading.append(element.text)
                # Extract and print the text from those elements
                result = {}
                result['url'] = url
                result['text'] = "".join(elements_before_heading)
                if result['text'] == "":
                    logging.exception(f"empty text while processing the {url}.")
                file_info['total'] += 1
                if not first['first']:
                    output_file.write(',\n')
                json.dump(result, output_file)
                del result
                first['first'] = False
                
            else:
                logging.exception(f"An exception occurred while processing the {url}.")
        else:
            logging.exception(f"can't request {url}.")
        
