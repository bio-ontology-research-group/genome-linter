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
        "db": "pmc",
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
        "db": "pmc",
        "id": pubmed_id,
        "retmode": "xml"
    }
    
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    
    # Parse PMC XML
    root = ET.fromstring(response.content)
    article = root.find(".//article")
    
    if article is None:
        return None
        
    title = article.find(".//article-title").text if article.find(".//article-title") is not None else ""
    
    # Extract full text sections
    body = article.find(".//body")
    full_text = ""
    if body is not None:
        full_text = " ".join([elem.text for elem in body.iter() if elem.text])
    
    authors = [
        (author.find(".//surname").text + " " + author.find(".//given-names").text).strip()
        for author in article.findall(".//contrib[@contrib-type='author']")
        if author.find(".//surname") is not None and author.find(".//given-names") is not None
    ]
    return {
        "pmcid": pubmed_id,
        "title": title,
        "full_text": full_text,
        "authors": authors
    }

def save_articles(articles: List[Dict], filename: str):
    """Save articles to JSON file"""
    with open(filename, "w") as f:
        json.dump(articles, f, indent=2)

def main():
    # Search for articles about genetic variants and rare diseases
    query = "(genetic variant) AND (rare disease)"
    article_ids = search_pubmed(query, 210000)
    print(f"Found {len(article_ids)} articles matching the query.")
    articles = []
    for i, pubmed_id in enumerate(article_ids):
        try:
            article = fetch_article_details(pubmed_id)
            if article:
                articles.append(article)
                print(f"Fetched article: {i + 1}/{len(article_ids)} {article['title']}")
                time.sleep(0.1)  # Be polite to PubMed servers
        except Exception as e:
            print(f"Error fetching article {pubmed_id}: {e}")
    
    # Save the collected articles
    save_articles(articles, "data/raw/pmc_articles.json")
    print(f"Saved {len(articles)} articles to data/raw/pmc_articles.json")

if __name__ == "__main__":
    main()