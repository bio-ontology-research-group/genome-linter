import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict

class ArticleRetriever:
    def __init__(self, index_path: str, metadata_path: str):
        """Initialize the retriever with existing vector store"""
        self.index = faiss.read_index(index_path)
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        """Retrieve top k most relevant articles for the query"""
        # Encode the query
        query_embedding = self.model.encode(query, convert_to_tensor=False)
        query_embedding = np.array([query_embedding]).astype('float32')
        
        # Search the index
        distances, indices = self.index.search(query_embedding, k)
        
        # Get the corresponding metadata
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0:  # FAISS returns -1 for invalid indices
                result = self.metadata[idx].copy()
                result["score"] = float(distances[0][i])
                results.append(result)
        
        return sorted(results, key=lambda x: x["score"])

def test_retrieval():
    """Test the retrieval system with sample queries"""
    retriever = ArticleRetriever(
        index_path="data/processed/vector_store.index",
        metadata_path="data/processed/vector_metadata.json"
    )
    
    test_queries = [
        "BRCA1 genetic variants in breast cancer",
        "Rare genetic disorders affecting metabolism",
        "Novel mutations in cystic fibrosis"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = retriever.retrieve(query)
        for i, result in enumerate(results):
            print(f"{i+1}. {result['title']} (Score: {result['score']:.2f})")
            print(f"   {result['text'][:100]}...")

if __name__ == "__main__":
    test_retrieval()