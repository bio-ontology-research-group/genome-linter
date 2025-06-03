#! /usr/bin/env python3

import json
import requests
import pandas as pd
import time

url = 'https://amelie.stanford.edu/api/gene_list_api/'


def main():

    df = pd.read_pickle('data/processed_amelie.pkl')
    with open('data/amelie_report.json') as f:
        results = json.loads(f.read())
    for i, row in df.iterrows():
        try:
            #print(f"Obtaining results for row {i+1} - {row['Patient Name']}")
            response = results[i]
            cause_gene = row['Causative gene']
            for rank, item in enumerate(response):
                if cause_gene == item[0]:
                    print(f"{row['Patient Name']}\t{cause_gene}\t{rank + 1}")
                    break
        except Exception as e:
            print(f"Error generating interpretation for row {i}: {e}")
    

if __name__ == "__main__":
    main()