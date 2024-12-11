from pymongo import MongoClient, ASCENDING
import logging 
import json 
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import torch

logging.getLogger('pymongo').setLevel(logging.WARNING)
BATCH_SIZE = 32
class DBInit:
    def __init__(self,device, data_info_path=None, data_info=None):

        client = MongoClient("localhost", 27017)
        self.db = client['db']
        
        if not data_info:
            data_info_file = open(data_info_path)
            self.data_info = json.load(data_info_file)
            data_info_file.close()
        else:
            self.data_info = data_info
        self.total_data = 0
        for info in self.data_info:
            self.total_data += info['total']


        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        self.device = device
        self.model.to(self.device)


    def populate_db(self, batch_size):
        batch_size = 1 if not batch_size else batch_size
        progress_bar = tqdm(total=self.total_data, desc=f"get embeddings", unit="step")
        current_id = 0
        for info in self.data_info:
            with open(info['path'], 'r', encoding='utf-8') as current_file:
                all_data = json.load(current_file)
            for i in range(0, info['total'], batch_size):
                data = all_data[i:min(i+batch_size, info['total'])]
                embeddings = self.model.encode([obj['text'] for obj in data])
                for k, embedding in enumerate(embeddings):
                    #data[k]['id'] = current_id
                    data[k]['embedding'] = embedding.tolist()
                    self.db['documents'].insert_one(data[k])
                    del data[k]['embedding']
                    current_id += 1
              
                del embeddings
                progress_bar.update(batch_size)

if __name__ == "__main__":
    """dbInit = DBInit(device=torch.device('cuda' if torch.cuda.is_available() else 'cpu'),
                data_info=[{'path' : r'c:\\Users\\matte\Desktop\\rag\\get_data\sample.json', "total" : 3000}])"""
    
    dbInit = DBInit(device=torch.device('cuda' if torch.cuda.is_available() else 'cpu'),
                data_info_path='get_data/data/data_info.json')
    dbInit.populate_db(batch_size=BATCH_SIZE)