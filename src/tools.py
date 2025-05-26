from camel.toolkits import FunctionTool
from retrieval.retriever import ArticleRetriever
import requests
import re
CLEANR = re.compile('<.*?>') 
from urllib.parse import quote

def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext

def genes_articles(genes: list) -> str:
    """Retrieve articles related to a specific gene and format the context for the model
    Args:
        genes (list): List of gene symbols to search for.
    Returns:
        str: Formatted context string containing article titles, authors, and abstracts.
    """
    retriever = ArticleRetriever()
    context = ""
    for gene in genes:
        articles = retriever.retrieve(gene)
        for article in articles:
            context += f"Title: {article['title']}\n"
            context += f"Authors: {', '.join(article['authors'])}\n"
            context += f"Abstract: {article['text']}\n\n"
    return context.strip()

genes_articles_tool = FunctionTool(genes_articles)


def aberowl_hpo(phenotype: str) -> str:
    """Retrieve background knowledge about a specific phenotype using AberOWL
    Args:
        phenotype (str): The phenotype to search for.
    Returns:
        str: Background knowledge about the phenotype.
    """
    phenotype = phenotype.strip().lower()
    print("Retrieving background knowledge about phenotype:", phenotype)
    response = requests.get(f"http://aber-owl.net/api/dlquery",
                            params=f"axioms=true&labels=true&type=equivalent&query=%27{quote(phenotype)}%27&ontology=HP")
    response.raise_for_status()
    data = response.json()
    if 'status' in data and data['status'] == 'ok' and len(data['result']) > 0:
        result = data['result'][0]
        result['id'] = result['class'].replace('http://purl.obolibrary.org/obo/HP_', 'HP:')
        result['SubClassOf'] = [cleanhtml(item) for item in result.get('SubClassOf', [])]
        return f"""phenotype: {result['label']} ({result['id']})\n
Definition: {', '.join(result.get('definition', [])) if 'definition' in result else 'No definition available'}\n
Synonyms: {', '.join(result.get('synonyms', [])) if 'synonyms' in result else 'No synonyms available'}\n
Subclass of: {', '.join(result.get('SubClassOf', [])) if 'SubClassOf' in result else 'No superclasses available'}\n"""
    return f"No background knowledge found for phenotype in AberOWL: {phenotype}"
aberowl_hpo_tool = FunctionTool(aberowl_hpo)