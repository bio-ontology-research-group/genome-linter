from collections import defaultdict
from agents import generate_interpretation
import argparse
import os

def main():
    # Initialize components
    retriever = ArticleRetriever()
    
    # Set up command line interface
    parser = argparse.ArgumentParser(description="VCF Analysis and Interpretation System for Genetic Variants")
    # Input options
    parser.add_argument("vcf", nargs='?', help="Input VCF file annotated with VEP (optional)")
    parser.add_argument("--genes", help="File containing list of genes (one per line)")
    parser.add_argument("--phenotypes", help="Phenotypes associated with the variants (comma-separated)")
    parser.add_argument("-o", "--output", help="Output report file", default="variant_report.md")
    parser.add_argument("--top_k", type=int, default=5, help="Total number of articles to retrieve (default: 3)")
    parser.add_argument("--openrouter_model", type=str, default="deepseek/deepseek-r1:free",
                       help="OpenRouter model to use (default: deepseek/r1:free)")
    args = parser.parse_args()
    
    # Parse VCF and find high-impact variants
    if not args.vcf and not args.ranked_genes:
        parser.error("Either VCF file or --ranked_genes must be provided")
    
    if not args.phenotypes:
        parser.error("Phenotypes must be provided")
    phenotypes = args.phenotypes.split(",")
    high_impact_genes = {}
    
    # Process VCF if provided
    if args.vcf:
        vcf_genes = process_vcf(args.vcf)
        if vcf_genes:
            high_impact_genes.update(vcf_genes)
        else:
            print("Note: No high-impact variants found in VCF")
    elif args.genes:
        ranked_genes = []
        print(args.genes)
        with open(args.genes, 'r') as f:
            ranked_genes = [line.strip() for line in f if line.strip()]
        # Create ordered dict preserving ranked order
        # Add ranked genes first
        for gene in ranked_genes:
            high_impact_genes[gene] = []
    print(high_impact_genes)
    # Get all genes for combined query
    genes = high_impact_genes.keys()
    if genes:
        print(f"Found {len(genes)} high-impact genes: {', '.join(genes)}")
        interpretation = generate_interpretation(
            genes=', '.join(genes),
            phenotypes=', '.join(phenotypes),
            model_type=args.openrouter_model
        )
        print("Generating interpretation...")
        with open(args.output, 'w') as report_file:
            report_file.write(interpretation)
    print(f"\nReport generated successfully: {args.output}")

def process_vcf(vcf_path: str) -> dict:
    """Parse VCF file and return genes with high-impact variants"""
    high_impact_consequences = {
        'transcript_ablation',
        'splice_acceptor_variant',
        'splice_donor_variant',
        'stop_gained',
        'frameshift_variant',
        'stop_lost'
    }
    
    genes = defaultdict(list)
    
    with open(vcf_path, 'r') as vcf:
        for line in vcf:
            if line.startswith('#'):
                continue
                
            fields = line.strip().split('\t')
            info = {k.split('=')[0]: k.split('=')[1] for k in fields[7].split(';') if '=' in k}
            
            if 'CSQ' not in info:
                continue
                
            for annotation in info['CSQ'].split(','):
                csq = annotation.split('|')
                consequence = csq[1]
                gene = csq[3]
                
                if consequence in high_impact_consequences:
                    genes[gene].append({
                        'chrom': fields[0],
                        'pos': fields[1],
                        'ref': fields[3],
                        'alt': fields[4],
                        'consequence': consequence
                    })
    
    return genes

if __name__ == "__main__":
    main()