from retrieval.retriever import ArticleRetriever
from generation.generator import AnswerGenerator
import argparse

def main():
    # Initialize components
    retriever = ArticleRetriever(
        index_path="data/processed/vector_store.index",
        metadata_path="data/processed/vector_metadata.json"
    )
    generator = AnswerGenerator()
    
    # Set up command line interface
    parser = argparse.ArgumentParser(description="PubMed RAG System for Genetic Variants and Rare Diseases")
    parser.add_argument("query", help="Your question about genetic variants and rare diseases")
    parser.add_argument("--top_k", type=int, default=3, help="Number of articles to retrieve (default: 3)")
    args = parser.parse_args()
    
    # Retrieve relevant articles
    print(f"\nSearching for articles related to: {args.query}")
    articles = retriever.retrieve(args.query, k=args.top_k)
    
    if not articles:
        print("No relevant articles found.")
        return
    
    # Display retrieved articles
    print("\nTop relevant articles:")
    for i, article in enumerate(articles):
        print(f"{i+1}. {article['title']}")
        print(f"   PubMed ID: {article['pubmed_id']}")
        print(f"   Authors: {', '.join(article['authors'])}")
        print(f"   Excerpt: {article['text'][:100]}...\n")
    
    # Generate answer
    print("Generating answer based on retrieved articles...")
    answer = generator.generate_answer(args.query, generator.format_context(articles))
    
    print("\nAnswer:")
    print(answer)

if __name__ == "__main__":
    main()