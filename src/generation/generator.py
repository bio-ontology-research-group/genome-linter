from typing import List, Dict, Optional
import requests
import os
import json

class OpenRouterGenerator:
    def __init__(self, model: str = "deepseek/deepseek-chat-v3-0324:free", api_key: Optional[str] = None):
        """Initialize with OpenRouter model"""
        self.model = model
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key not provided and OPENROUTER_API_KEY environment variable not set")
        
    def format_context(self, articles: List[Dict]) -> str:
        """Format retrieved articles as context for the generator"""
        context = ""
        for article in articles:
            context += f"Title: {article['title']}\n"
            context += f"Authors: {', '.join(article['authors'])}\n"
            context += f"Abstract: {article['text']}\n\n"
        return context.strip()
    
    def generate_answer(self, genes: str, phenotypes: str, context: str) -> str:
        """Generate answer using OpenRouter API"""
        prompt = f"""You are a clinical geneticist analyzing research about genetic variants and rare diseases.
Based on these scientific articles:

{context}

Question: Which of the following genes with high impact variants are directly or indirectly relevant for {phenotypes}, rank them and interpret the evidence. Just answer the question.:
{genes}
Answer:"""
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-Return-Billing": "true",
                "HTTP-Referer": "http://borg.kaust.edu.sa",  # Required by some OpenRouter models
                "X-Title": "Genome Linter"  # Optional app identifier
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 100000
            }
        )
        response.raise_for_status()
        response_data = response.json()
        gen_id = response_data.get("id", None)
        url = f"https://openrouter.ai/api/v1/generation?id={gen_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        stats = response.json()
        cost = stats["data"].get("total_cost", 0)
        print(f"OpenRouter request cost: ${cost:.4f}")
        return response_data["choices"][0]["message"]["content"]


def test_generation():
    """Test the generation system with sample queries"""
    test_articles = [
        {
            "title": "BRCA1 mutations in hereditary breast cancer",
            "authors": ["Smith J", "Doe R"],
            "text": "The BRCA1 gene has been identified as a major risk factor for hereditary breast cancer. Several pathogenic variants have been characterized."
        }
    ]
    
    # Test local generator
    test_genes = "BRCA1, TP53"
    test_phenotypes = "breast cancer"
    # Test OpenRouter generator if API key available
    if os.getenv("OPENROUTER_API_KEY"):
        print("Testing OpenRouter generator...")
        openrouter_generator = OpenRouterGenerator()
        context = openrouter_generator.format_context(test_articles)
        answer = openrouter_generator.generate_answer(test_genes, test_phenotypes, context)
        print(f"Genes: {test_genes}, Phenotype: {test_phenotypes}")
        print(f"Answer: {answer}")
    else:
        print("OpenRouter API key not set, skipping OpenRouter generator test.")

if __name__ == "__main__":
    test_generation()