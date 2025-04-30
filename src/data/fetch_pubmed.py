import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import time
from typing import List, Dict
import json

def search_pubmed(query: str, max_results: int = 100) -> List[str]:
    """Search PubMed and return article IDs matching the query"""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json"
    }
    
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()
    
    return data.get("esearchresult", {}).get("idlist", [])

def fetch_article_details(pubmed_id: str) -> Dict:
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
        "abstract": abstract,
        "authors": authors
    }

def save_articles(articles: List[Dict], filename: str):
    """Save articles to JSON file"""
    with open(filename, "w") as f:
        json.dump(articles, f, indent=2)

def main():
    # Search for articles about genetic variants and rare diseases
    query = "(genetic variant) AND (rare disease)"
    article_ids = search_pubmed(query, 10000)
    
    articles = []
    for pubmed_id in article_ids:
        try:
            article = fetch_article_details(pubmed_id)
            if article:
                articles.append(article)
                print(f"Fetched article: {article['title']}")
                time.sleep(0.1)  # Be polite to PubMed servers
        except Exception as e:
            print(f"Error fetching article {pubmed_id}: {e}")
    
    # Save the collected articles
    save_articles(articles, "data/raw/pubmed_articles.json")
    print(f"Saved {len(articles)} articles to data/raw/pubmed_articles.json")

if __name__ == "__main__":
    main()