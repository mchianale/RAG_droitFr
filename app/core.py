from pymongo import MongoClient, ASCENDING
import numpy as np
from fastapi import HTTPException
import numpy as np 
from sentence_transformers import SentenceTransformer
import time 
from tqdm import tqdm

class QueryService:
    def __init__(self, device):
        # MongoDB setup
        self.client = MongoClient("localhost", 27017)
        self.db = self.client['db']
        self.collection_centroid = self.db['centroids']
        self.collection_doc = self.db['documents']

        self.centroids = None
        if 'centroids' in self.db.list_collection_names():
            self.centroids = np.array([centroid['embedding'] for centroid in list(self.db['centroids'].find())])
        # setpu the model  
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        self.device = device
        self.model.to(self.device)
        
        # can compute query:
        self.canQuery = True if self.centroids is not None and self.centroids.shape[0] > 0 else False
    
    def _checkCanQuery(self):
        if not self.canQuery:
            raise HTTPException(status_code=404, detail="You need to create clusters first,\npost (example) = /clusterize?n_clusters=15&max_iter=300&tolerance=1e-4&patience=10")

    def _encode(self, query : str):
        return np.array(self.model.encode(query))
    
    def _getMatchingCentroids(self, embedding):
        cosine_similarities = np.dot(self.centroids, embedding) / (
            np.linalg.norm(self.centroids, axis=1) * np.linalg.norm(embedding)
        )
        sorted_indices = np.argsort(cosine_similarities)[::-1]
        return sorted_indices

    def _getMatchingDocuments(self, embedding, embeddings):
        cosine_similarities = np.dot(embeddings, embedding) / (
            np.linalg.norm(embeddings, axis=1) * np.linalg.norm(embedding)
        )
        top_indices = np.argsort(cosine_similarities)[::-1]
        return top_indices, cosine_similarities

    def query_documents(self, query: str, limit: int = 10):
        self._checkCanQuery()
        # Encode input query
        embedding = self._encode(query=query)
        # get the best centroid matching
        closest_centroid_index = int(self._getMatchingCentroids(embedding=embedding)[0])
        matching_documents = list(self.collection_doc.find({"cluster_id": closest_centroid_index}))
        if not matching_documents:
            raise HTTPException(status_code=404, detail="No documents found")
        
        embeddings = np.array([doc['embedding'] for doc in matching_documents])
        top_indices, cosine_similarities = self._getMatchingDocuments(embedding=embedding, embeddings=embeddings) # Sort and reverse for descending order
        top_indices = top_indices[:limit]
        top_matching_documents = [
            {'text': matching_documents[i]['text'], 'cosine_similarity': float(cosine_similarities[i])}
            for i in top_indices
        ]
        return top_matching_documents

    def clusterize(self,n_clusters, max_iter, tolerance, patience):
        start_time = time.time()
        # init
        centroids = np.array([doc['embedding'] for doc in self.collection_doc.aggregate([{'$sample': {'size': n_clusters}}])])
        ids = list(self.collection_doc.find({}, {'_id': 1}))
    
        labels = np.zeros(len(ids))
        unchanged_iter_count = 0  # Counter for iterations without significant change

        for iteration in range(max_iter):
            # Step 3.1: Assign each point to the closest centroid
            i = 0
            all_cluster_points = [[] for _ in range(n_clusters)]
            for id in tqdm(ids, desc=f'iteration {iteration}'):
                current_doc = self.collection_doc.find_one({'_id': id['_id']})
                #distances = np.linalg.norm(np.array(current_doc['embedding']) - centroids, axis=1)  # Calculate distance to each centroid
                current_doc_embedding = np.array(current_doc['embedding'])
                cosine_similarities = np.dot(centroids, current_doc_embedding) / (np.linalg.norm(centroids, axis=1) * np.linalg.norm(current_doc_embedding))
                cosine_distances = 1 - cosine_similarities
                labels[i] = np.argmin(cosine_distances)  # Assign the closest centroid
                all_cluster_points[int(labels[i])].append(id['_id'])
                i += 1

            # Step 3.2: Update the centroids
            new_centroids = np.zeros_like(centroids)
            for j in range(n_clusters):
                cluster_points = np.array([doc['embedding'] for doc in self.collection_doc.find({"_id": {"$in": all_cluster_points[j]}})])
                if cluster_points.shape[0] > 0:
                    new_centroids[j] = np.mean(cluster_points, axis=0) 
            
            # Step 3.3: Check for convergence (if centroids don't change, stop early)
            centroid_change = np.linalg.norm(new_centroids - centroids)  # Calculate the change in centroids
            if centroid_change < tolerance:
                unchanged_iter_count += 1
            else:
                unchanged_iter_count = 0

            # If the centroids haven't changed significantly for 'patience' iterations, stop early
            if unchanged_iter_count >= patience:
                #print(f"Converged after {iteration + 1} iterations.")
                break

            # Update centroids for the next iteration
            centroids = new_centroids

            # If the centroid change is small, we can also stop early.
            if centroid_change < tolerance:
                #print(f"Converged after {iteration + 1} iterations.")
                break
             
        # udpate 
        self.centroids = centroids
        self.canQuery = True if self.centroids is not None and self.centroids.shape[0] > 0 else False

        if 'centroids' in self.db.list_collection_names():
            self.collection_centroid.delete_many({})

        # add centroids to db   
        for i in range(centroids.shape[0]):
            self.collection_centroid.insert_one({
                'cluster_id' : i,
                'embedding' : centroids[i].tolist()
            })
            # update documents 
            self.collection_doc.update_many(
                {"_id": {"$in": all_cluster_points[i]}},  # Find documents where the 'id' is in ids_to_update
                {"$set": {"cluster_id": i}}      # Add or update the 'cluster_id' field to j
            )

        self.collection_centroid.create_index([('cluster_id', ASCENDING)], unique=True)
        self.collection_doc.create_index([('cluster_id', ASCENDING)])
       
        end_time = time.time()
        return {"message" : f"Converged after {iteration + 1} iterations.", "elapsed time (min)" : (end_time - start_time) / 60}

    def createDoc(self, doc):
        try:
            doc['embedding'] = self._encode(query=doc['text'])
            if self.canQuery:
                # get the best centroid matching
                doc['cluster_id'] = int(self._getMatchingCentroids(embedding=doc['embedding'])[0])
            doc['embedding'] = doc['embedding'].tolist()
        except:
            HTTPException(status_code=404, detail="Invalid format for the input document")
    

    def insertOneDocument(self, doc):   
        self.createDoc(doc)
        self.collection_doc.insert_one(doc)
        return {"message" : "successfully add a new document"}
    
    def insertManyDocuments(self, docs):
        self.collection_doc.insert_many(docs)
        return {"message" : f"successfully add {len(docs)} new documents"}
    
    def evaluateClusters(self, threshold):
        self._checkCanQuery()
        start_time = time.time()
        mean_cosine = 0
        tp, fp, tn, fn = 0, 0, 0, 0
        total = 0
        labels = [i for i in range(self.collection_centroid.count_documents({}))]
        already_compare = [[0 for _ in range(len(labels))] for _ in range(len(labels))]

        for idx1 in tqdm(labels):
            docs_idx1 = list(self.collection_doc.find({"cluster_id": idx1}))
            for idx2 in labels:
                if already_compare[idx1][idx2] == 1:
                    continue
                already_compare[idx1][idx2] = 1
                already_compare[idx2][idx1] = 1

                docs_idx2_embeddings = np.array([doc['embedding'] for doc in list(
                    self.collection_doc.find(
                        {"cluster_id": idx2},   
                        {"embedding": 1}        
                    )
                )])
                
                for i, doc1 in enumerate(docs_idx1):
                    embedding = np.array(doc1['embedding'])
                    cosine_similarities = np.dot(docs_idx2_embeddings,embedding ) / (
                        np.linalg.norm(docs_idx2_embeddings, axis=1) * np.linalg.norm(embedding)
                    )
            
                    for j, cosine_sim in enumerate(cosine_similarities):
                        if idx1 == idx2 and i == j:
                            continue
                        if idx1 == idx2:
                            if cosine_sim >= threshold:
                                tp += 1 
                            else: 
                                fp += 1 
                        else:
                            if cosine_sim >= threshold:
                                fn += 1 
                            else:
                                tn += 1 
                        mean_cosine += cosine_sim
                        total += 1
                        
        precision = tp/(tp+fp) * 100
        recall = tp/(tp+fn) * 100
        f1 = 2* (precision*recall)/(precision+recall) 
        end_time = time.time()

        return {
            "precision" : precision,
            "recall" : recall,
            "f1" : f1,
            "mean_cosine" : mean_cosine/total,
            "elapsed time (min)" : (end_time - start_time) / 60,
            "total_data" : self.collection_doc.count_documents({})
        }
    
    def reset(self):
        self.collection_doc.delete_many({})
        self.collection_centroid.delete_many({})
        return {"message" :  f"successfully reset the db"}
    
    def getInfo(self):
        result = {}
        total_data = 0
        if self.centroids is not None and self.centroids.shape[0] > 0:
            clusters_info = []
            for cluster in list(self.collection_centroid.find({})):
                number_docs = self.collection_doc.count_documents({'cluster_id': cluster['cluster_id']})
                total_data += number_docs
                clusters_info.append({f"cluster_{cluster['cluster_id']}" : number_docs})
            result['clusters'] = clusters_info
        else:
            total_data = self.collection_doc.count_documents({})
        result['total_data'] = total_data
        return result


