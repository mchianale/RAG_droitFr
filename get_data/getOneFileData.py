import os
import json 

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))  # this file path
DATA_PATH = os.path.join(SCRIPT_PATH, 'data') # main & global data path
OUTPUT_PATH = 'data'


def load_json(file_path):
    """ Load JSON data from a file. """
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error loading {file_path}: {e}")
            return None

def explore_and_collect_jsons(path):
    """ Recursively explore a directory for JSON files and collect their contents. """
    collected_data = []
    
    # Walk through all the directories and files in the given path
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.json'):  # Check if the file is a JSON file
                file_path = os.path.join(root, file)
                data = load_json(file_path)
                
                if data is not None:
                    # If the JSON file contains a list, append each element
                    if isinstance(data, list):
                        collected_data.extend(data)
                    else:
                        collected_data.append(data)

    return collected_data


output_file = open(OUTPUT_PATH, 'w')
output_file.write('[\n')