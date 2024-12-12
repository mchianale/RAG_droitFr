from fastapi import FastAPI
from app.core import QueryService
import torch
from typing import Dict, List
from threading import Thread


# Initialize FastAPI app and QueryService
app = FastAPI()
query_service = QueryService(device=torch.device('cuda' if torch.cuda.is_available() else 'cpu'))

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

# Define routes
@app.get("/query")
async def query_documents(query: str, limit: int = 10):
    """
    GET route to query documents by cluster_id.
    Args:
        query (str): input text
        limit (int): Number of documents to return. Default is 10.
    Returns:
        List of documents that match the query.
    """
    return query_service.query_documents(query=query, limit=limit)

@app.post("/clusterize")
async def clusterize(n_clusters: int, chunk_size: int = 1000):
    return query_service.clusterize(n_clusters=n_clusters, chunk_size=chunk_size)

@app.post("/insert_new_document")
async def insert_new_document(doc : Dict):
    return query_service.insertOneDocument(doc=doc)


@app.post("/insert_new_documents")
async def insert_new_document(docs : List[Dict], chunk_size : int = 32):
    threads = []
    for i in range(0, len(docs), chunk_size):
        for doc in docs[i:i+chunk_size]:
            thread = Thread(target=query_service.createDoc, args=(doc,))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        threads = []
        query_service.insertManyDocuments(docs=docs[i:i+chunk_size])
    return {"message" : f"successfully add {len(docs)} new documents"}

@app.get("/evaluate_clusters")
async def evaluate_clusters(threshold: float = 0.9):
    return query_service.evaluateClusters(threshold=threshold)

@app.post("/reset")
async def reset():
    return query_service.reset()

@app.get("/info")
async def info():
    return query_service.getInfo()