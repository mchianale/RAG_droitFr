from init_code import getCodeData
from init_corpus import get_article_links
from funct.functs import delete_folder 
import json
import os 
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))  # this file path
DATA_PATH = os.path.join(SCRIPT_PATH, 'data/all_data')
INFO_PATH = os.path.join(SCRIPT_PATH, 'data/data_info.json')


delete_folder(DATA_PATH)

print('STEP 1: retrouver les articles des codes en vigueur : https://www.legifrance.gouv.fr/liste/code?etatTexte=VIGUEUR&etatTexte=VIGUEUR_DIFF&page=1#code')
all_info = getCodeData()
print("STEP 2: creer un corpus d'articles lié au droit")
already_article_links = []
max_workers = 20
base_roots = ["Droit Français"]
# Get all article links
for base_root in base_roots:
    info, already_article_links = get_article_links(base_root, already_article_links=already_article_links, max_workers=max_workers)
    all_info += info

total = 0
for info in all_info:
    total += info['total']
file = open(INFO_PATH, 'w')
json.dump(all_info, file)
file.close()
print(f"Total number of data': {total}")