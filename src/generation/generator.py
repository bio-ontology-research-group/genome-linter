from typing import List, Dict
from transformers import pipeline
import torch

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
    
    generator = AnswerGenerator()
    context = generator.format_context(test_articles)
    
    test_query = "What is the significance of BRCA1 variants in breast cancer?"
    answer = generator.generate_answer(test_query, context)
    
    print(f"Question: {test_query}")
    print(f"Answer: {answer}")

if __name__ == "__main__":
    test_generation()