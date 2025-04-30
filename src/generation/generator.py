from typing import List, Dict, Optional
from transformers import pipeline
import torch
import requests
import os

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
            context += f"Abstract: {article['text'][:500]}...\n\n"
        return context.strip()
    
    def generate_answer(self, query: str, context: str) -> str:
        """Generate answer using OpenRouter API"""
        prompt = f"""You are a clinical geneticist analyzing research about genetic variants and rare diseases.
Based on these scientific articles:

{context}

Question: {query}
Answer:"""
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 1000
            }
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

class AnswerGenerator:
    def __init__(self, model_name: str = "facebook/bart-large-mnli"):
        """Initialize the answer generator with a smaller language model"""
        self.generator = pipeline(
            "text-generation",
            model=model_name,
            device=0 if torch.cuda.is_available() else -1,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        
    def format_context(self, articles: List[Dict]) -> str:
        """Format retrieved articles as context for the generator"""
        context = ""
        for article in articles:
            context += f"Title: {article['title']}\n"
            context += f"Authors: {', '.join(article['authors'])}\n"
            context += f"Abstract: {article['text'][:500]}...\n\n"  # Truncate long abstracts
        return context.strip()
    
    def generate_answer(self, query: str, context: str) -> str:
        """Generate an answer to the query based on the provided context"""
        prompt = f"""Based on the following scientific articles, answer the question:

{context}

Question: {query}
Answer:"""
        
        # Generate the answer with more conservative settings
        result = self.generator(
            prompt,
            max_new_tokens=200,  # Use max_new_tokens instead of max_length
            num_return_sequences=1,
            temperature=0.5,
            do_sample=True,
            truncation=True,
            pad_token_id=self.generator.tokenizer.eos_token_id
        )
        
        return result[0]['generated_text'].split("Answer:")[-1].strip()

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
    print("Testing local generator...")
    local_generator = AnswerGenerator()
    context = local_generator.format_context(test_articles)
    test_query = "What is the significance of BRCA1 variants in breast cancer?"
    answer = local_generator.generate_answer(test_query, context)
    print(f"Question: {test_query}")
    print(f"Answer: {answer}\n")
    
    # Test OpenRouter generator if API key available
    if os.getenv("OPENROUTER_API_KEY"):
        print("Testing OpenRouter generator...")
        openrouter_generator = OpenRouterGenerator()
        answer = openrouter_generator.generate_answer(test_query, context)
        print(f"Question: {test_query}")
        print(f"Answer: {answer}")

if __name__ == "__main__":
    test_generation()