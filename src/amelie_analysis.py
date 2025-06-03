import pandas as pd
import random
import json
import os
import pickle



def process_data():
    # Load data files
    ddd_df = pd.read_csv('data/amelie_ddd.csv')
    with open('data/genes.txt') as f:
        all_genes = [line.strip() for line in f.readlines()]
    
    gene_data = []
    
    for _, row in ddd_df.iterrows():
        # Get required number of candidate genes
        num_candidates = row['Number of candidate causative genes']
        causative_gene = row['Causative gene']
        
        # Filter genes with available data
        valid_genes = [
            g for g in all_genes
            if g != causative_gene
            and os.path.exists(f"data/genes/{g}.json")
        ]
        
        # Ensure minimum candidate count
        try:
            selected = random.sample(valid_genes, min(num_candidates-1, len(valid_genes)))
        except ValueError:
            selected = []
            
        # Always include causative gene and remove duplicates
        candidates = list(set(selected + [causative_gene]))
        random.shuffle(candidates)
        
        # Load articles and track missing genes
        data = []
        missing_genes = []
        for gene in candidates:
            json_path = f"data/genes/{gene}.json"
            try:
                with open(json_path) as f:
                    data.append({
                        'gene': gene,
                        'articles': json.load(f),
                    })
            except FileNotFoundError:
                print(f"File not found: {json_path}")
                missing_genes.append(gene)
        
        # Log missing genes
        if missing_genes:
            with open('missing_genes.log', 'a') as log:
                log.write(f"{row['Patient Name']}: {', '.join(missing_genes)}\n")
        
        # Store results
        gene_data.append(data)
    
    ddd_df['gene_data'] = gene_data
    # Save to pickle
    ddd_df.to_pickle('data/processed_amelie.pkl')
    print(ddd_df)
    
if __name__ == '__main__':
    process_data()