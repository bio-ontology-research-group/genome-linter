import json
import re
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import numpy as np

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove special characters and normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s-]', '', text)
    return text.strip()

def chunk_text(text: str, max_length: int = 512) -> List[str]:
    """Split text into chunks of max_length tokens"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= max_length:
            current_chunk.append(word)
            current_length += len(word) + 1
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def process_articles(input_file: str, output_file: str):
    """Process raw PubMed articles into chunks ready for embedding"""
    with open(input_file, 'r') as f:
        articles = json.load(f)
    
    processed = []
    for article in articles:
        # Clean and chunk the full text
        full_text = clean_text(article.get('full_text', ''))
        chunks = chunk_text(full_text)
        
        for i, chunk in enumerate(chunks):
            processed.append({
                "pmcid": article["pmcid"],
                "title": article["title"],
                "chunk_id": i,
                "text": chunk,
                "authors": article["authors"],
                "source": "pmc"
            })
    
    # Save processed articles
    with open(output_file, 'w') as f:
        json.dump(processed, f, indent=2)
    
    print(f"Processed {len(articles)} articles into {len(processed)} chunks")

if __name__ == "__main__":
    process_articles(
        input_file="data/raw/pmc_articles.json",
        output_file="data/processed/articles_chunks.json"
    )