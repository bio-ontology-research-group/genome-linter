from camel.toolkits import FunctionTool
from retrieval.retriever import ArticleRetriever
def gene_articles(gene: str) -> str:
    """Retrieve articles related to a specific gene and format the context for the model
    Args:
        gene (str): The gene symbol to search for.
    Returns:
        str: Formatted context string containing article titles, authors, and abstracts.
    """
    retriever = ArticleRetriever()
    articles = retriever.retrieve(gene)
    context = ""
    for article in articles:
        context += f"Title: {article['title']}\n"
        context += f"Authors: {', '.join(article['authors'])}\n"
        context += f"Abstract: {article['text']}\n\n"
    return context.strip()

gene_articles_tool = FunctionTool(gene_articles)