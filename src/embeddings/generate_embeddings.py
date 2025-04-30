import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import os

class VectorStore:
    def __init__(self, embedding_dim: int = 768): # Updated dimension for all-mpnet-base-v2
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim) # Use updated dimension
        self.metadata = []
        self.model = SentenceTransformer('all-mpnet-base-v2') # Updated model
        
    def add_documents(self, documents: List[Dict]):
        """Add documents to the vector store"""
        texts = [doc["text"] for doc in documents]
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        
        # Add to FAISS index
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Store metadata
        self.metadata.extend(documents)
        
    def save(self, index_path: str, metadata_path: str):
        """Save the index and metadata"""
        faiss.write_index(self.index, index_path)
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
            
    @classmethod
    def load(cls, index_path: str, metadata_path: str):
        """Load existing index and metadata"""
        store = cls()
        store.index = faiss.read_index(index_path)
        with open(metadata_path, 'r') as f:
            store.metadata = json.load(f)
        return store

def generate_embeddings(input_file: str, index_path: str, metadata_path: str):
    """Generate embeddings for processed articles and save to vector store"""
    with open(input_file, 'r') as f:
        processed_articles = json.load(f)
    
    # Initialize vector store
    vector_store = VectorStore()
    
    # Add documents in batches
    batch_size = 32
    for i in range(0, len(processed_articles), batch_size):
        batch = processed_articles[i:i + batch_size]
        vector_store.add_documents(batch)
        print(f"Processed {min(i + batch_size, len(processed_articles))}/{len(processed_articles)} articles")
    
    # Save the vector store
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    vector_store.save(index_path, metadata_path)
    print(f"Saved vector store with {len(processed_articles)} embeddings")

if __name__ == "__main__":
    generate_embeddings(
        input_file="data/processed/articles_chunks.json",
        index_path="data/processed/vector_store.index",
        metadata_path="data/processed/vector_metadata.json"
    )