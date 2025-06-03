from collections import defaultdict
from retrieval.retriever import ArticleRetriever
from generation.generator import OpenRouterGenerator
import argparse
import os
import click as ck
import pandas as pd
from agents import generate_interpretation

@ck.command()
@ck.option('--openrouter_model', default='deepseek/deepseek-chat-v3-0324:free', help='OpenRouter model to use')
@ck.option('--output', default='data/report.txt', help='Report output file')
def main(openrouter_model, output):
    # Initialize appropriate generator
    generator = OpenRouterGenerator(openrouter_model)
    index = [3, 12, 18, 21, 57, 62, 74, 102, 113, 121, 142, 147, 178, 179, 183, 184, 201]
    df = pd.read_pickle('data/processed_amelie.pkl').iloc[index]
    interpretations = []
    report = open(output, 'w')
    for i, row in df.iterrows():
        try:
            phenotypes = row['Phenotype names']
            gene_data = row['gene_data']
            genes = []
            for item in gene_data:
                genes.append(item['gene'])
            combined_genes = ', '.join(genes)
            interpretation = generate_interpretation(
                combined_genes,
                phenotypes,
            )
            report.write(f"## Patient {i+1} - {row['Patient Name']}\n")
            report.write(f"### Causative Gene: {row['Causative gene']}\n")
            report.write(f"### Phenotypes: {phenotypes}\n")
            report.write(f"### Genes: {combined_genes}\n")
            report.write(f"### Clinical Interpretation\n{interpretation}\n\n")
        except Exception as e:
            print(f"Error generating interpretation for row {i}: {e}")
            interpretations.append("Error generating interpretation")
    report.close()
    print(f"Report saved to {output}")
    
if __name__ == "__main__":
    main()