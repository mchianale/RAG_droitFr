import os
import json 
import random
from tqdm import tqdm

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))  # this file path
SAMPLE_PATH = os.path.join(SCRIPT_PATH, 'sample.json')
INFO_PATH = os.path.join(SCRIPT_PATH, 'data/data_info.json')
N = 3000

def create_sample(size, sample_path):
    data_info_file = open(INFO_PATH, 'r',encoding='utf-8')
    data_info = json.load(data_info_file)
    data_info_file.close()

    output_file = open(sample_path, 'w')
    output_file.write('[\n')
    first = True
    potential = [[i for i in range(info['total'])] for info in data_info]
    index = [i for i in range(len(potential))]
    for _ in tqdm(range(size), desc='Generate sample'):
        if len(index) == 0:
            break
        #print(index)
        random_file_index = random.choice(index)
        random_obj_index = random.choice(potential[random_file_index])
        if len(potential[random_file_index]) == 1:
            index.remove(random_file_index)
        else:
            potential[random_file_index].remove(random_obj_index)
        current_file = open(data_info[random_file_index]['path'])
        current_obj = json.load(current_file)[random_obj_index]
        current_file.close()
        if not first:
            output_file.write(',\n')
        else:
            first = False 
        json.dump(current_obj, output_file)
    output_file.write('\n]')
    output_file.close()
        
create_sample(size=N, sample_path=SAMPLE_PATH)
