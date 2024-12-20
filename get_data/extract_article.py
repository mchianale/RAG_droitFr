import fitz  # PyMuPDF
import json
import os
from tqdm import tqdm
import logging
import random

# Configure logging
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))  # this file path
DATA_PATH = os.path.join(SCRIPT_PATH, 'data/all_data')
# Configure logging
log_file_path = os.path.join(SCRIPT_PATH, 'data/log/error_log.txt')
# Erase previous log content by opening in write mode
with open(log_file_path, 'w') as log_file:
    pass 
logging.basicConfig(
    filename=os.path.join(log_file_path),  # Name of the log file
    level=logging.ERROR,       # Log level to capture errors and above
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format of log messages
)
def create_folder(folder_path):
    # If the folder exists, delete it and all its contents
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def updateParts(parts, start):
    for i in range(start, len(parts)):
        parts[i] = None
    return parts


def read_pdf_with_formatting(file_path, code, info):
    
    # create code folder
    #output_path = os.path.join(base_output_path, code.lower().strip().replace(" ", "_"))
    #create_folder(output_path)
    code_id = code.lower().replace(' ', '_') + str(random.randint(1, 100))
    output_path = os.path.join(DATA_PATH, f"{code_id}.json")
    output_file = open(output_path, 'w')
    output_file.write('[\n')
    first = True
    
     
    doc = fitz.open(file_path)
    parts = [None, None, None, None, None, None, None]
    names = ["partie", "livre", "titre", "chapitre", "section", "sous-section", "paragraphe"]
    article_name, current_article = "", ""
    last_update = None
    for page_num in tqdm(range(len(doc)), desc=code):
        page = doc.load_page(page_num)
        #print(f"\nPage {page_num + 1}:")
        
        # Extract text blocks with position and font info
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if block['type'] == 0:  # Check if the block is text (not an image)
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span['text'].replace("\n", "").strip()
                        font_size = span['size']
                        if len(text) < 2:
                            continue

                        elif font_size == 8:
                            continue

                        elif font_size == 14:
                            if article_name != "" and current_article != "":
                                # add a new article 
                                article_obj = {"code" : code}
                                for i in range(len(parts)):
                                    if not parts[i]:
                                        continue
                                    article_obj[names[i]] = parts[i]
                                article_obj["article"] = article_name.replace("*", "_")
                                article_obj["text"] = current_article
                                #print('-'*100 + '\n' + str(article_obj) + '\n'+ '-'*100)
                                if not first:
                                    output_file.write(',\n')
                                else:
                                    first = False
                                json.dump(article_obj, output_file)
                                info['total'] += 1
                                

                            current_article = ""
                            article_name = text

                        elif font_size == 16:
                            first_letter = text[0]
                            if first_letter == "C" and text[1] != "h":
                                continue

                            if article_name != "" and current_article != "":
                                # add a new article 
                                article_obj = {"code" : code}
                                for i in range(len(parts)):
                                    if not parts[i]:
                                        continue
                                    article_obj[names[i]] = parts[i]
                                article_obj["article"] = article_name.replace("*", "_")
                                article_obj["text"] = current_article
                                #print('-'*100 + '\n' + str(article_obj) + '\n'+ '-'*100)
                                if not first:
                                    output_file.write(',\n')
                                else:
                                    first = False
                                json.dump(article_obj, output_file)
                                info['total'] += 1
                                
                                
                                
                            current_article = ""
                            article_name = ""

                            if first_letter == "P":
                                if "aragraphe" in text:
                                    parts = updateParts(parts=parts, start=6)
                                    parts[-1] = text
                                    last_update = -1
                                else:
                                    parts = updateParts(parts=parts, start=1)
                                    parts[0] = text
                                    last_update = 0
                            elif first_letter == "L":
                                parts = updateParts(parts=parts, start=2)
                                parts[1] = text
                                last_update = 1
                            elif first_letter == "T":
                                parts = updateParts(parts=parts, start=3)
                                parts[2] = text
                                last_update = 2
                            elif first_letter == "C":
                                parts = updateParts(parts=parts, start=4)
                                parts[3] = text 
                                last_update = 3
                            elif first_letter == "S":
                                if "-" in text:
                                    parts[5] = text
                                    last_update = 5
                                else:
                                    parts = updateParts(parts=parts, start=5)
                                    parts[4] = text
                                    last_update = 4
                            elif last_update is not None:
                                parts[last_update] += text

                        elif text != "":
                            last_update = None
                            current_article += '\n' + text

    # add last article
    if article_name != "" and current_article != "":
        article_obj = {"code" : code}
        for i in range(len(parts)):
            if not parts[i]:
                continue
            article_obj[names[i]] = parts[i]
        article_obj["article"] = article_name.replace("*", "_")
        article_obj["text"] = current_article
        if not first:
            output_file.write(',\n')
        else:
            first = False
        json.dump(article_obj, output_file)
        info['total'] += 1
    
    output_file.write('\n]')          
    output_file.close() 
    info['path'] = output_path
       
