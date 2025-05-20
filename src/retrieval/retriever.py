from typing import List, Dict
import numpy as np
import requests
import xml.etree.ElementTree as ET
import time
import json
import os
class ArticleRetriever:
    def __init__(self):
        """Initialize the retriever with PubMed API integration"""
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        
    def search_pubmed(self, query: str, max_results: int = 100) -> List[str]:
        """Search PubMed and return article IDs matching the query"""
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance",
        }
        
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return data.get("esearchresult", {}).get("idlist", [])

    def fetch_article_details(self, pubmed_id: str) -> Dict:
        """Fetch detailed information for a single PubMed article"""
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": pubmed_id,
            "retmode": "xml"
        }
        
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        article = root.find(".//PubmedArticle")
        
        if article is None:
            return None
            
        title = article.find(".//ArticleTitle").text if article.find(".//ArticleTitle") is not None else ""
        abstract = article.find(".//AbstractText").text if article.find(".//AbstractText") is not None else ""
        authors = [author.find(".//LastName").text + " " + author.find(".//ForeName").text 
                for author in article.findall(".//Author") 
                if author.find(".//LastName") is not None and author.find(".//ForeName") is not None]
        
        return {
            "pubmed_id": pubmed_id,
            "title": title,
            "text": abstract,
            "authors": authors
        }

    def retrieve(self, gene: str, k: int = 5) -> List[Dict]:
        """Retrieve top k most relevant articles from PubMed"""
        # Check if the gene articles have already been retrieved
        if os.path.exists(f"data/genes/{gene}.json"):
            print(f"Skipping {gene} (already retrieved)")
            with open(f"data/genes/{gene}.json", "r") as f:
                return json.load(f)
        # Search PubMed and fetch articles
        article_ids = self.search_pubmed(gene, k)
        # Introduce a delay to avoid hitting the API too quickly
        time.sleep(0.1)                
        articles = []
        for pubmed_id in article_ids:
            try:
                article = self.fetch_article_details(pubmed_id)
                # Introduce a delay to avoid hitting the API too quickly
                time.sleep(0.1)                
                if article:
                    articles.append(article)
            except Exception as e:
                print(f"Error fetching article {pubmed_id}: {e}")
        # Save articles to a file
        with open(f"data/genes/{gene}.json", "w") as f:
            json.dump(articles, f, indent=4)
        return  articles

    def expand_query(self, gene: str) -> str:
        """Expand query with PubMed search syntax"""
        expansion = f'("{gene} protein, human"[Supplementary Concept] OR "{gene} protein, human"[All Fields] OR "{gene}"[All Fields] OR "genes, {gene}"[MeSH Terms] OR ("genes"[All Fields] AND "{gene}"[All Fields]) OR "{gene} genes"[All Fields]) AND variants[All Fields] AND ("disease"[MeSH Terms] OR "disease"[All Fields] OR "diseases"[All Fields])'
        return expansion

def test_retrieval():
    """Test the PubMed retrieval system with sample queries"""
    retriever = ArticleRetriever()
    
    test_queries = [
        "BRCA1",
        "MUC1"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = retriever.retrieve(query)
        for i, result in enumerate(results):
            print(f"{i+1}. {result['title']} ")

def retrieve_for_all_genes():
    """Retrieve articles for a list of genes"""
    retriever = ArticleRetriever()
    
    # with open("data/genes.list", "r") as f:
    #     genes = [line.strip() for line in f.readlines()]
    genes = ['C5orf42',]
    for i, gene in enumerate(genes):
        try:
            if os.path.exists(f"data/genes/{gene}.json"):
                print(f"Skipping {gene} (already retrieved)")
                continue
            print(f"Retrieving articles for {gene} ({i + 1} / {len(genes)})...")
            articles = retriever.retrieve(gene)
            # Save articles to a file
            with open(f"data/genes/{gene}.json", "w") as f:
                json.dump(articles, f, indent=4)
        except Exception as e:
            print(f"Error retrieving articles for {gene}: {e}")
            time.sleep(0.5)

if __name__ == "__main__":
    #test_retrieval()
    retrieve_for_all_genes()